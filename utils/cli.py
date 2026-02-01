import argparse
import sys

from utils.constants import (
    CLI_DEFAULT_MAX_RESULTS_IN_GROUP,
    CSV_DATA_DEFAULT_DELIMITER,
    CSV_DATA_DEFAULT_MC_DELIMITER,
    DEFAULT_RESULTS_PRECISION,
)


def _type_precision_integer(value):
    try:
        integer_value = int(value)
    except:
        raise argparse.ArgumentTypeError("must be an integer (>=-1)")

    if integer_value < -1:
        raise argparse.ArgumentTypeError("must be an integer (>=-1)")
    return integer_value


def _type_positive_integer(value):
    try:
        integer_value = int(value)
    except:
        raise argparse.ArgumentTypeError("must be a positive integer (>=1)")

    if integer_value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer (>=1)")
    return integer_value


class _CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"Error: {message}\n")
        sys.stderr.write("Use -h or --help for more information.\n")
        # self.print_help()
        sys.exit(2)


def get_parser():
    PARSER = _CustomArgumentParser(
        prog="Valentine matcher",
        description="Match fellow classmates, colleagues or anyone else based on their answers to form questions and generate beautiful html and pdf result files!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""If you wish to know how to format the csv data file, what headings are required and how to correctly specify them, please refer to this project's README.md\nAll information besides on how to use this program is specified in this project's README.md file.\n\nThis is Weekintas from CS50x""",
    )
    PARSER.add_argument(
        "in_file",
        help="Filename of the formatted csv data file (make sure to format it according to information in README.md)",
        metavar="filename",
    )
    PARSER.add_argument(
        "formats",
        nargs="+",  # one or more
        type=str.upper,
        choices=("PDF", "EMAIL"),
        metavar="FORMAT",
        help='Output format(s); specify one or both: "PDF" "EMAIL"',
    )

    PARSER.add_argument(
        "--delimiter",
        default=CSV_DATA_DEFAULT_DELIMITER,
        metavar="CHAR",
        help='Delimiter character for the CSV file (default: "%(default)s") which separates cells',
    )
    PARSER.add_argument(
        "--multi-delimiter",
        default=CSV_DATA_DEFAULT_MC_DELIMITER,
        metavar="CHAR",
        help='Delimiter character for the CSV file (default: "%(default)s") which separates multiple options in a single cell',
    )
    PARSER.add_argument(
        "-o",
        "--output-dir",
        default="out/generated_result_files/",
        help='The directory path in which to put all generated result files (default: "out/generated_result_files/")',
    )
    PARSER.add_argument(
        "-p",
        "--precision",
        type=_type_precision_integer,
        default=DEFAULT_RESULTS_PRECISION,
        metavar="NUM",
        help='Number of decimal places to round results to (default: "%(default)s"). Specify -1 to not round at all (not recommended).',
    )
    PARSER.add_argument(
        "-s",
        "--separate-by-groups",
        action="store_true",
        help="Separate output files into folders by respondent groups",
    )
    PARSER.add_argument(
        "-m",
        "--max-results-in-group",
        type=_type_positive_integer,
        default=CLI_DEFAULT_MAX_RESULTS_IN_GROUP,
        metavar="NUM",
        help="Maximum number of matches per group (default: %(default)s)",
    )
    PARSER.add_argument(
        "--on-file-exists",
        choices=("override", "ask", "skip"),
        default="ask",
        metavar="MODE",
        help='What to do if an output file exists: "override", "ask", or "skip" (default: "%(default)s")',
    )

    return PARSER
