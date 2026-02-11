import sys
import time

import tabulate
from email_sending.send_email import send_result_email
from utils.classes.email_attachment import EmailAttachment
from utils.datetime import now_str
import utils.sql as SQL
import utils.filesystem as utils


def handle_mail(args):
    match args.action.lower():
        case "send":
            send_mail(
                args.project_id,
                args.email_type,
                args.recipients,
                args.recipients_from_database,
                args.subject,
                args.body_path,
                args.body_from_database,
                args.attachments,
                args.database_attachments,
                not args.dont_halt_on_fail,
            )
        case "status":
            pass  # TODO: implement
        case _:
            raise ValueError(f"Invalid action '{args.action}' in 'mail' command")


def send_mail(
    project_id: str,
    email_type: str,
    recipients: list[str] | None,
    recipients_from_db: bool,
    subject: str,
    body_path: str | None,
    body_from_db: str | None,
    attachments: list[str] | None,
    attachments_db: list[str] | None,
    halt_on_fail: bool,
):
    if recipients and recipients_from_db:
        raise ValueError("Both '--recipients' and '--recipients-from-database' can not be specified. Specify only one.")
    if not recipients and not recipients_from_db:
        raise ValueError(
            "Neither '--recipients' nor '--recipients-from-database' are specified specified. Please specify one and only one."
        )

    if body_path and body_from_db:
        raise ValueError("Both '--body-path' and '--body-from-database' can not be specified. Specify only one.")
    if not body_path and not body_from_db:
        raise ValueError(
            "Neither '--body-path' nor '--body-from-database' are specified specified. Please specify one and only one."
        )

    # if no attachments are provided check if that is true
    if not attachments and not attachments_db:
        user_input = input(f"No attachments were provided. Do you wish to continue [y/N]?").lower()
        if user_input != "y":
            print("Not sending any emails.")
            return
    # if halt on fail is disabled, check if that is true
    if not halt_on_fail:
        user_input = input(f"Halting on any fail is disabled. Do you wish to continue [y/N]?").lower()
        if user_input != "y":
            print("Not sending any emails.")
            return

    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)

    # get recipient list
    if recipients:
        sql_cursor.execute(
            "SELECT * FROM respondents WHERE project_id = ? AND email IN ?", (project_sql_id, recipients)
        )
        recipients_info = sql_cursor.fetchall()
        recipient_emails = [resp["email"] for resp in recipients_info]
        if len(recipient_emails) != len(recipients):
            raise ValueError(
                f"One or more recipient email addresses are not connected to any respondents in the database. All emails sent must be sent to respondents that are defined in this project."
            )
    else:
        sql_cursor.execute("SELECT * FROM respondents WHERE project_id = ?", (project_sql_id,))
        recipients_info = sql_cursor.fetchall()
        recipient_emails = [resp["email"] for resp in recipients_info]

    # if there are some respondents with no emails sent, ask if should still send
    if recipient_emails.count(None) > 0:
        user_input = input(
            f"There are {recipient_emails.count(None)} recipients without email addresses. Would you like to continue sending emails, but only to recipients with valid email addresses [y/N]? "
        ).lower()
        if user_input == "n" or user_input != "y":
            print("Not sending any emails.")
            return

    # get the body path
    if body_path:
        html_body_paths = {r["id"]: body_path for r in recipients_info}
    else:
        sql_cursor.execute(
            "SELECT respondent_id, path, sha256, size_bytes FROM generated_files WHERE project_id = ? AND file_type = ?",
            (project_sql_id, body_from_db),
        )
        files_info = sql_cursor.fetchall()
        if len(files_info) != len(recipient_emails):
            raise ValueError(
                f"The amount of recipients ({len(recipient_emails)}) does not match the number of email html body files stored in database ({len(files_info)})."
            )

        html_body_paths = {}
        for file_info in files_info:
            try:
                # TODO: this method is costly and dumb of checking if id exista and getting it
                id = next(resp["id"] for resp in recipients_info if resp["id"] == file_info["respondent_id"])
            except StopIteration:
                raise ValueError(
                    f"Email html body file not found in database for respondent with id '{file_info['respondent_id']}'"
                )

            # check if file exists and credentials are ok
            file_path = file_info["path"]
            file_exists, file_hash, file_size = SQL.get_file_info(file_path)
            if not file_exists:
                raise ValueError(f"Email html body file not found in filesystem for respondent at path '{file_path}'")
            if file_hash != file_info["sha256"]:
                raise ValueError(f"Email html body file has a different hash than expected: '{file_path}'")
            if file_size != file_info["size_bytes"]:
                raise ValueError(f"Email html body file has a different size than expected: '{file_path}'")

            # file exists and is ok, add to the list
            html_body_paths[id] = file_path

    # get list of attachments
    recipients_attachments: dict[str, list[EmailAttachment]] = {}
    if attachments:
        for attachment in attachments:
            if not utils.file_exists(attachment):
                raise ValueError(f"Attachment at path '{attachment}' does not exist.")
    for recipient_info in recipients_info:
        recipient_attachments: list[EmailAttachment] = []
        if attachments:  # TODO: Figure out custom naming the email attachment from list cli
            recipient_attachments = [
                # TODO: fix naming here
                EmailAttachment(
                    attachment,
                    filename=f"Rezultatai {"pdf" if attachment.endswith(".pdf") else "foto"} - {recipient_info['name']}",
                )
                for attachment in attachments
            ]

        if attachments_db:  # TODO: Figure out custom naming the email attachment from db
            sql_cursor.execute(
                "SELECT path, sha256, size_bytes FROM generated_files WHERE project_id = ? AND respondent_id = ? AND file_type IN (%s)"
                % ",".join("?" * len(attachments_db)),
                (project_sql_id, recipient_info["id"], *attachments_db),
            )
            for attachment_info in sql_cursor.fetchall():
                path = attachment_info["path"]
                file_exists, file_hash, file_size = SQL.get_file_info(path)
                if not file_exists:
                    raise ValueError(f"Email attachment not found in filesystem for respondent at path '{path}'")
                if file_hash != attachment_info["sha256"]:
                    raise ValueError(f"Email attachment has a different hash than expected: '{path}'")
                if file_size != attachment_info["size_bytes"]:
                    raise ValueError(f"Email attachment has a different size than expected: '{path}'")

                # TODO: fix naming here
                recipient_attachments.append(
                    EmailAttachment(
                        path,
                        filename=f"Rezultatai {"pdf" if path.endswith(".pdf") else "foto"} - {recipient_info['name']}",
                    )
                )

        recipients_attachments[recipient_info["id"]] = recipient_attachments

    # send emails
    should_send = print_to_be_sent_emails_and_ask(subject, recipients_info, html_body_paths, recipients_attachments)
    if not should_send:
        print("Not sending any emails.")
        sys.exit(0)

    recipient_amount = len(recipients_info)

    for i, recipient_info in enumerate(recipients_info, 1):
        id = recipient_info["id"]
        email = recipient_info["email"]
        if not email:
            print(
                f"({i}/{recipient_amount}) Email NOT SENT to {recipient_info['name']} (id: {id}) because their EMAIL ADDRESS IS NOT SPECIFIED."
            )
            continue

        html_body_path = html_body_paths[id]
        attachment_list = recipients_attachments[id]

        response_ok, status_code, response_json = send_result_email(email, html_body_path, subject, attachment_list)

        sql_cursor.execute(
            "SELECT COUNT(*) AS count FROM emails WHERE project_id = ? AND respondent_id = ? AND email_type = ?",
            (project_sql_id, id, email_type),
        )
        email_previously_sent = sql_cursor.fetchone()["count"] > 0
        if email_previously_sent:
            print(
                f"Recipient (id: {id}, name: {recipient_info['name']}, email: {email}) has already received an email of type: '{email_type}'."
            )
            if halt_on_fail:
                print("Halting all further email sending.")
                sys.exit(1)
            else:
                print("Continuing anyway (halting on fail is disabled).")

        if response_ok:
            print(f"({i}/{recipient_amount}) Email successfully sent to {email}.")
        else:
            print(f"ERROR ({i}/{recipient_amount}): Email not sent to {email}: {response_json}.")

        # save the email send data to database
        sql_cursor.execute(
            "INSERT INTO emails (project_id, respondent_id, email_type, status, status_code, response_json, body_html_path, attachment_paths, sent_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                project_sql_id,
                id,
                email_type,
                "SUCCESS" if response_ok else "FAIL",
                status_code,
                str(response_json),
                html_body_path,
                ", ".join([attachment.filepath for attachment in attachment_list]),
                now_str(),
            ),
        )
        sql_connection.commit()

        if halt_on_fail and not response_ok:
            print("Halting all further email sending.")
            sys.exit(1)


def print_to_be_sent_emails_and_ask(subject, recipients_info, html_body_paths, recipients_attachments) -> bool:
    print(f"EMAIL SUBJECT: '{subject}'")

    tabulate_rows = []
    for recipient in recipients_info:
        attachments = recipients_attachments.get(recipient["id"], [])

        tabulate_rows.append(
            {
                "id": recipient["id"],
                "name": recipient["name"],
                "email": recipient["email"],
                "html_body_path": html_body_paths[recipient["id"]],
                "attachments": ", ".join(f"{a.filepath} | {a.filename}" for a in attachments),
            }
        )
    print(tabulate.tabulate(tabulate_rows, headers="keys", tablefmt="grid"))

    user_input = input(
        f"Are you sure you want to send these emails to {len(recipients_info)} recipients [y/n]? "
    ).lower()
    if user_input != "y":
        return False

    # on confirm wait 15 seconds and ask to re-confirm
    print("Please wait 15 seconds and then re-confirm your choice...")
    time.sleep(15)

    user_input = input(
        f"Are you VERY MUCH SURE you want to SEND THESE EMAILS to {len(recipients_info)} recipients? After this there is NO GOING BACK (except CTRL+C in an emergency) [yes/no] "
    ).lower()
    return user_input == "yes"
