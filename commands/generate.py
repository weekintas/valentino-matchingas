from program_input_handling.process_py_config_file import process_py_config_file
from program_input_handling.read_csv_input_data import read_data_from_csv
from results.generate_all import generate_result_files
from utils.classes.match_table import MatchTable
from utils.classes.matchmaking_config import MatchmakingConfig
from utils.classes.result_file_type import ResultFileType
from utils.datetime import now_str
import utils.sql as SQL
import sys


def handle_generate(args):
    project_id = args.project_id
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    # get program config and match_groups from processing config file if given
    sql_cursor.execute(
        "SELECT csv_path, csv_delimiter, csv_multi_delimiter FROM projects WHERE code = ?", (project_id,)
    )
    path, delimeter, multi_delimeter = sql_cursor.fetchone()[0:]
    group_codes, _, respondents = read_data_from_csv(path, delimeter, multi_delimeter, verbose=True)
    try:
        cli_config = MatchmakingConfig.from_argparse_args(args)
        program_config, match_groups = process_py_config_file(args.config_path, cli_config, group_codes)
    except Exception as e:
        print(
            "----------------------------------------------------------------\n"
            "AN ERROR OCCURRED WHILE READING DATA FROM THE PYTHON CONFIG FILE\n"
            "----------------------------------------------------------------\n"
            f"Error: {e}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)
    user_input = input(f"Would you like to store generated files' information to the database? [Y/n]? ").lower()
    if user_input == "n":
        generate_files(match_groups, respondents, sql_cursor, project_id, args.formats, program_config)
        sql_connection.close()
        print("Result files not stored in the database.")
        return
    elif user_input != "y":
        sql_connection.close()
        print("No files were generated nor stored in the database.")
        return

    #  check if there are already files generated in db
    # TODO: Here result filke type mismatch between sql and other places, messy
    file_types_to_be_generated = [ResultFileType.from_string(f_type).to_sql_type_str() for f_type in args.formats]
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)
    sql_cursor.execute(
        "SELECT COUNT(*) AS count FROM generated_files WHERE project_id = ? AND file_type IN (%s)"
        % ",".join("?" * len(file_types_to_be_generated)),
        (project_sql_id, *file_types_to_be_generated),
    )
    num_files = sql_cursor.fetchone()["count"]
    if num_files > 0:
        user_input = input(
            f"There are already {num_files} generated file database rows for these file types: '{"', '".join(file_types_to_be_generated)}'. Are you sure you want to override all files of THESE types? [y/N/exit]? "
        ).lower()
        if user_input == "n":
            generate_files(match_groups, respondents, sql_cursor, project_id, args.formats, program_config)
            sql_connection.close()
            print("Result files not stored in the database.")
            return
        if user_input != "y":
            sql_connection.close()
            print("No files were generated nor stored in the database.")
            return

        sql_cursor.execute(
            "DELETE FROM generated_files WHERE project_id = ? AND file_type IN (%s)"
            % ",".join("?" * len(file_types_to_be_generated)),
            (project_sql_id, *file_types_to_be_generated),
        )
        sql_connection.commit()

    # generate result files based on file types selected
    filepaths = generate_files(match_groups, respondents, sql_cursor, project_id, args.formats, program_config)

    # format list of tuples for batch sql execution
    files_info = []
    for i, (f_type, path, resp) in enumerate(filepaths):
        _, file_hash, file_size = SQL.get_file_info(path)
        files_info.append(
            (
                project_sql_id,
                resp.id,
                f_type.to_sql_type_str(),
                path,
                file_hash,
                file_size,
                now_str(),
            )
        )
    sql_cursor.executemany(
        "INSERT INTO generated_files (project_id, respondent_id, file_type, path, sha256, size_bytes, created_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
        files_info,
    )
    sql_connection.commit()
    sql_connection.close()

    print(f"Successfully saved ({len(filepaths)}) generated file data into the database.")


def generate_files(match_groups, respondents, sql_cursor, project_id, formats: list[str], program_config):
    try:
        filepaths = generate_result_files(
            match_groups,
            respondents,
            MatchTable.from_database(sql_cursor, project_id, len(respondents)),
            [ResultFileType.from_string(f_type) for f_type in formats],
            config=program_config,
            verbose=True,
        )
        return filepaths
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
