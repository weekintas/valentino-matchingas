import sys

from classes.result_file_type import ResultFileType
from csv_io.read_csv import read_data_from_csv
from matching.match_all import match_all_respondents
from results.pdf_results.generate_all import generate_result_files
from utils.cli import get_parser


def main():
    # init args for easy use
    args = get_parser().parse_args()

    # read csv data
    try:
        questions_data, respondent_dict = read_data_from_csv(
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

    # match respondents
    try:
        match_table = match_all_respondents(list(respondent_dict.values()), questions_data)
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
            match_table,
            respondent_dict,
            [ResultFileType.from_string(f_type) for f_type in args.formats],
            precision=args.precision,
            max_num_of_results_in_group=args.max_results_in_group,
            output_dir=args.output_dir,
            separate_into_group_dirs=args.separate_by_groups,
            file_exists_behaviour=args.on_file_exists,
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
