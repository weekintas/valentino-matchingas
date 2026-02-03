import sys

from classes.matchmaking_config import MatchmakingConfig
from classes.result_file_type import ResultFileType
from program_input_handling.process_py_config_file import process_py_config_file
from program_input_handling.read_csv_input_data import read_data_from_csv
from matching.match_all import match_all_respondents
from results.generate_all import generate_result_files
from utils.cli import get_parser


def main():
    # init args for easy use
    args = get_parser().parse_args()
    cli_program_config = MatchmakingConfig.from_argparse_args(args)

    # read csv data
    try:
        group_codes, questions_data, all_respondents = read_data_from_csv(
            args.in_file, delimiter=args.delimiter, multi_delimiter=args.multi_delimiter, verbose=True
        )
    except Exception as e:
        print(
            "------------------------------------------------------------\n"
            "AN ERROR OCCURRED WHILE READING DATA FROM THE CSV FILE GIVEN\n"
            "------------------------------------------------------------\n"
            f"Error: {e}\n"
            "Make sure to:\n"
            " * Check that the input file exists\n"
            " * Check that the data file has a header at the very first line, contains all required headings, and that all other headings are correctly formatted.\n"
            " * Check that the 'delimiter' specified is correct and correctly placed/escaped everywhere in the file.\n"
            " * Check that the 'multi-delimiter' specified is correct and correctly placed/escaped everywhere in the file.\n"
            " * If you did not explicitly specify the delimiter and/or multi-delimiter, check that the default values for those are correct (run -h to see the default values).",
            file=sys.stderr,
        )
        sys.exit(1)

    # process config file if given
    try:
        program_config, match_groups = process_py_config_file(args.config_path, cli_program_config, group_codes)
    except Exception as e:
        print(
            "----------------------------------------------------------------\n"
            "AN ERROR OCCURRED WHILE READING DATA FROM THE PYTHON CONFIG FILE\n"
            "----------------------------------------------------------------\n"
            f"Error: {e}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # match respondents
    try:
        match_table = match_all_respondents(all_respondents, questions_data)
    except Exception as e:
        print(
            "--------------------------------------------\n"
            "AN ERROR OCCURRED WHILE MATCHING RESPONDENTS\n"
            "--------------------------------------------\n"
            f"Error: {e}\n"
            "Make sure to:\n"
            " * Check that the csv data file is correctly formatted, and that each data cell is aligned with the correct header (especially in respondents' answers to questions)",
            file=sys.stderr,
        )
        sys.exit(1)

    # generate result files based on file types selected
    try:
        generate_result_files(
            match_groups,
            all_respondents,
            match_table,
            [ResultFileType.from_string(f_type) for f_type in args.formats],
            config=program_config,
            verbose=True,
        )
    except Exception as e:
        print(
            "-----------------------------------------------\n"
            "AN ERROR OCCURRED WHILE GENERATING RESULT FILES\n"
            "-----------------------------------------------\n"
            f"Error: {e}\n"
            "Make sure to:\n"
            " * Check that jinja2 is installed\n"
            " * Check that pdfkit and wkhtmltopdf are properly installed",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
