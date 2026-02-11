# import sys

# from utils.classes.matchmaking_config import MatchmakingConfig
# from utils.classes.result_file_type import ResultFileType
# from program_input_handling.process_py_config_file import process_py_config_file
# from program_input_handling.read_csv_input_data import read_data_from_csv
# from matching.match_all import match_all_respondents
# from results.generate_all import generate_result_files
# from utils.cli import get_parser


# def main():
#     # init args for easy use
#     args = get_parser().parse_args()
#     cli_program_config = MatchmakingConfig.from_argparse_args(args)

#     # read csv data
#     try:
#         group_codes, questions_data, all_respondents = read_data_from_csv(
#             args.in_file, delimiter=args.delimiter, multi_delimiter=args.multi_delimiter, verbose=True
#         )
#     except Exception as e:
#         print(
#             "------------------------------------------------------------\n"
#             "AN ERROR OCCURRED WHILE READING DATA FROM THE CSV FILE GIVEN\n"
#             "------------------------------------------------------------\n"
#             f"Error: {e}\n"
#             "Make sure to:\n"
#             " * Check that the input file exists\n"
#             " * Check that the data file has a header at the very first line, contains all required headings, and that all other headings are correctly formatted.\n"
#             " * Check that the 'delimiter' specified is correct and correctly placed/escaped everywhere in the file.\n"
#             " * Check that the 'multi-delimiter' specified is correct and correctly placed/escaped everywhere in the file.\n"
#             " * If you did not explicitly specify the delimiter and/or multi-delimiter, check that the default values for those are correct (run -h to see the default values).",
#             file=sys.stderr,
#         )
#         sys.exit(1)

#     # process config file if given
#     try:
#         program_config, match_groups = process_py_config_file(args.config_path, cli_program_config, group_codes)
#     except Exception as e:
#         print(
#             "----------------------------------------------------------------\n"
#             "AN ERROR OCCURRED WHILE READING DATA FROM THE PYTHON CONFIG FILE\n"
#             "----------------------------------------------------------------\n"
#             f"Error: {e}\n",
#             file=sys.stderr,
#         )
#         sys.exit(1)

#     # match respondents
#     try:
#         match_table = match_all_respondents(all_respondents, questions_data)
#     except Exception as e:
#         print(
#             "--------------------------------------------\n"
#             "AN ERROR OCCURRED WHILE MATCHING RESPONDENTS\n"
#             "--------------------------------------------\n"
#             f"Error: {e}\n"
#             "Make sure to:\n"
#             " * Check that the csv data file is correctly formatted, and that each data cell is aligned with the correct header (especially in respondents' answers to questions)",
#             file=sys.stderr,
#         )
#         sys.exit(1)

#     # generate result files based on file types selected
#     try:
#         generate_result_files(
#             match_groups,
#             all_respondents,
#             match_table,
#             [ResultFileType.from_string(f_type) for f_type in args.formats],
#             config=program_config,
#             verbose=True,
#         )
#     except Exception as e:
#         print(
#             "-----------------------------------------------\n"
#             "AN ERROR OCCURRED WHILE GENERATING RESULT FILES\n"
#             "-----------------------------------------------\n"
#             f"Error: {e}\n"
#             "Make sure to:\n"
#             " * Check that jinja2 is installed\n"
#             " * Check that pdfkit and wkhtmltopdf are properly installed",
#             file=sys.stderr,
#         )
#         sys.exit(1)


# if __name__ == "__main__":
#     main()

# TODO: Implement NO_RESPONSE for groups which are not needed
# TODO: fix whatever the fuck is going on with RESULTS_EMAIL and result file type mismatch between sql and classes enum values
# TODO: when generating files, it only saves data to sql after all of them are generated, and should save after each file creation as to avoid loss of sql data when program interrupted while generating
# TODO: pdf and png templates main have one tiny difference

import argparse
import sys
import re

from commands.project import handle_project
from commands.match import handle_match
from commands.generate import handle_generate
from commands.mail import handle_mail
from commands.doctor import handle_doctor
from utils.cli import _type_positive_integer, _type_precision_integer
from utils.constants import (
    CLI_DEFAULT_MAX_RESULTS_IN_GROUP,
    CSV_DATA_DEFAULT_DELIMITER,
    CSV_DATA_DEFAULT_MULTI_DELIMITER,
    DEFAULT_RESULTS_PRECISION,
)


def main():
    # Starts and ends with alphanumeric, no consecutive dashes
    PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")

    def project_id(value: str) -> str:
        """
        Validate a project ID:
        - Only letters, numbers, and single dashes
        - Must start and end with letter or number
        - No consecutive dashes
        """
        if not PROJECT_ID_RE.fullmatch(value):
            raise argparse.ArgumentTypeError(
                "Project ID must contain only letters, numbers, and single dashes, "
                "cannot start or end with a dash, and cannot have consecutive dashes."
            )
        return value

    class CustomArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write(f"Error: {message}\n")
            sys.stderr.write("Use -h or --help for more information.\n")
            # self.print_help()
            sys.exit(2)

    parser = CustomArgumentParser(
        prog="Valentine matchmaker",
        description="Match fellow classmates, colleagues or anyone else based on their answers to form questions and generate beautiful html and pdf result files!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""If you wish to know how to format the csv data file, what headings are required and how to correctly specify them, please refer to this project's README.md\nAll information besides on how to use this program is specified in this project's README.md file.\n\nThis is Weekintas""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- project ----
    project_parser = subparsers.add_parser("project")
    project_sub = project_parser.add_subparsers(dest="action", required=True)

    project_create = project_sub.add_parser("create")
    project_create.add_argument("project_id", type=project_id)
    project_create.add_argument("csv_path")
    project_create.add_argument("--name")
    project_create.add_argument("--description")
    project_create.add_argument(
        "--delimiter",
        metavar="CHAR",
        default=CSV_DATA_DEFAULT_DELIMITER,
        help='Delimiter character for the CSV file (default: "%(default)s") which separates cells',
    )
    project_create.add_argument(
        "--multi-delimiter",
        metavar="CHAR",
        default=CSV_DATA_DEFAULT_MULTI_DELIMITER,
        help='Delimiter character for the CSV file (default: "%(default)s") which separates multiple options in a single cell',
    )

    project_delete = project_sub.add_parser("delete")
    project_delete.add_argument("project_id", type=project_id)

    project_sub.add_parser("list")

    project_create = project_sub.add_parser("reset_csv")
    project_create.add_argument("project_id", type=project_id)
    project_create.add_argument("csv_path")

    # ---- match ----
    match_parser = subparsers.add_parser("match")
    match_parser.add_argument("project_id", type=project_id)

    # ---- generate ----
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("project_id", type=project_id)
    generate_parser.add_argument(
        "formats",
        nargs="+",  # one or more
        type=str.upper,
        choices=("PDF", "EMAIL", "PNG"),
        metavar="FORMAT",
        help='Output format(s); specify one or more: "PDF" "EMAIL" "PNG',
    )
    generate_parser.add_argument(
        "-c",
        "--config-path",
        default=None,
        metavar="CONFIG_PATH",
        help="Path to a python config file",
    )
    generate_parser.add_argument(
        "--delimiter",
        default=CSV_DATA_DEFAULT_DELIMITER,
        metavar="CHAR",
        help='Delimiter character for the CSV file (default: "%(default)s") which separates cells',
    )
    generate_parser.add_argument(
        "--multi-delimiter",
        default=CSV_DATA_DEFAULT_MULTI_DELIMITER,
        metavar="CHAR",
        help='Delimiter character for the CSV file (default: "%(default)s") which separates multiple options in a single cell',
    )
    generate_parser.add_argument(
        "-o",
        "--output-dir",
        default="out/generated_result_files/",
        help='The directory path in which to put all generated result files (default: "out/generated_result_files/")',
    )
    generate_parser.add_argument(
        "--precision",
        type=_type_precision_integer,
        default=DEFAULT_RESULTS_PRECISION,
        metavar="NUM",
        help='Number of decimal places to round results to (default: "%(default)s"). Specify -1 to not round at all (not recommended).',
    )
    generate_parser.add_argument(
        "--separate-by-groups",
        action="store_true",
        help="Separate output files into folders by respondent groups",
    )
    generate_parser.add_argument(
        "--max-results-in-group",
        type=_type_positive_integer,
        default=CLI_DEFAULT_MAX_RESULTS_IN_GROUP,
        metavar="NUM",
        help="Maximum number of matches per group (default: %(default)s)",
    )
    generate_parser.add_argument(
        "--on-file-exists",
        choices=("override", "ask", "skip"),
        default="ask",
        metavar="MODE",
        help='What to do if an output file exists: "override", "ask", or "skip" (default: "%(default)s")',
    )

    # ---- mail ----
    mail_parser = subparsers.add_parser("mail")
    mail_sub = mail_parser.add_subparsers(dest="action", required=True)

    mail_send = mail_sub.add_parser("send")
    mail_send.add_argument("project_id", type=project_id)
    mail_send.add_argument(
        "email_type",
        # nargs="+",  # one or more
        type=str.upper,
        choices=("REGISTER_CONFIRM", "RESULTS"),
        metavar="TYPE",
        help="REGISTER_CONFIRM - registration confirmation email. RESULTS - matchmaking results.",
    )
    mail_send.add_argument(
        "-r",
        "--recipients",
        nargs="+",
        help="One or more email addresses of all recipients. If specified, --recipients-from-database must not be specified.",
    )
    mail_send.add_argument(
        "--recipients-from-database",
        action="store_true",
        help="Whether to mail all recipients stored in the database for the project. If specified, --recipients must not be specified.",
    )
    mail_send.add_argument("-s", "--subject", help="Subject of all emails sent.", required=True)
    mail_send.add_argument(
        "-b",
        "--body-path",
        metavar="PATH",
        help="Path to the html file that will be used as the body of all emails sent. If specified, --body-from-database must not be specified.",
    )
    mail_send.add_argument(
        "--body-from-database",
        type=str.upper,
        choices=("RESULTS_EMAIL",),
        help="Specofy to use dinamically files from database as email bodies. Value specified is the 'file_type' from database. Currently supported types: 'RESULTS_EMAIL'.",
    )
    mail_send.add_argument(
        "-a",
        "--attachments",
        nargs="+",
        help="Path to one or more files that will be sent as attachments in all emails.",
    )
    mail_send.add_argument(
        "--database-attachments",
        nargs="+",
        type=str.upper,
        choices=("RESULTS_PDF", "RESULTS_PNG"),
        metavar="GENERATED_FILE_TYPES",
        help="The types of generated files from database to send as attachments to recipients. Currently supports types: 'RESULTS_PDF' and 'RESULTS_PNG'.",
    )
    mail_send.add_argument(
        "--dont-halt-on-fail",
        action="store_true",
        help="Whether to continue sending emails to all other recipients after one fails being sent.",
    )

    mail_status = mail_sub.add_parser("status")
    mail_status.add_argument("project_id", type=project_id)

    # ---- doctor ----
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("project_id", type=project_id)

    args = parser.parse_args()

    # ---- execute ----
    if args.command == "project":
        handle_project(args)
    elif args.command == "match":
        handle_match(args)
    elif args.command == "generate":
        handle_generate(args)
    elif args.command == "mail":
        handle_mail(args)
    elif args.command == "doctor":
        handle_doctor(args)


if __name__ == "__main__":
    main()
