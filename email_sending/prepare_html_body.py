def format_email_html_body(html_body: str):
    return html_body.replace("\n", "").replace('"', "'")


def get_email_html_body(html_filepath):
    with open(html_filepath, "r", encoding="UTF-8") as file:
        unformatted_body = file.read()

    formatted_body = format_email_html_body(unformatted_body)
    return formatted_body
