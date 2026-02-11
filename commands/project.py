from utils.datetime import now_str
import utils.sql as SQL


def handle_project(args):
    match args.action.lower():
        case "create":
            create_project(
                args.project_id, args.csv_path, args.name, args.description, args.delimiter, args.multi_delimiter
            )
        case "delete":
            delete_project(args.project_id)
        case "list":
            list_projects()
        case "reset_csv":
            reset_csv(args.project_id, args.csv_path)
        case _:
            raise ValueError(f"Invalid action '{args.action}' in 'project' command")


def create_project(project_id: str, csv_path: str, name: str, description: str, delimiter: str, multi_delimiter: str):
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    # check if a project already exists with this id
    if SQL.project_exists(sql_cursor, project_id):
        sql_connection.close()
        raise ValueError(f"Project with id '{project_id}' already exists.")

    # check if csv_path points to a valid file
    csv_exists, csv_hash, csv_size = SQL.get_file_info(csv_path)
    if not csv_exists:
        sql_connection.close()
        raise ValueError(f"Csv data file at '{csv_path}' does not exist.")

    # create project in database
    sql_cursor.execute(
        "INSERT INTO projects (code, name, description, csv_path, csv_sha256, csv_size, csv_delimiter, csv_multi_delimiter, created_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (project_id, name, description, csv_path, csv_hash, csv_size, delimiter, multi_delimiter, now_str()),
    )
    sql_connection.commit()

    # print messages
    SQL.fetch_and_print(
        sql_cursor,
        "SELECT code AS id, name, description, csv_path, csv_delimiter AS delimiter, csv_multi_delimiter AS multi_delimiter, created_at FROM projects WHERE code = ?",
        (project_id,),
        message="Project created!",
    )

    # write respondent data
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)
    _, _, respondents = SQL.read_csv_data_file(sql_cursor, project_id)
    for resp in respondents:
        sql_cursor.execute(
            "INSERT INTO respondents (id, project_id, name, email, gender, csv_data) VALUES(?, ?, ?, ?, ?, ?)",
            (resp.id, project_sql_id, resp.full_name, resp.email, str(resp.gender), resp.csv_data_row),
        )
    sql_connection.commit()
    print(f"Wrote {len(respondents)} respondents' data into the database.")

    sql_connection.close()


def delete_project(project_id: str):
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    # check if a project already exists with this id
    if not SQL.project_exists(sql_cursor, project_id):
        sql_connection.close()
        raise ValueError(f"Project with id '{project_id}' does not exist.")

    # get the project id stored in sql
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)

    # count everything associated with this project
    counts: dict[str, int] = {}
    sql_cursor.execute("SELECT COUNT(*) AS count FROM respondents WHERE project_id = ?", (project_sql_id,))
    counts["respondents"] = sql_cursor.fetchone()["count"]
    sql_cursor.execute("SELECT COUNT(*) AS count FROM match_results WHERE project_id = ?", (project_sql_id,))
    counts["matches"] = sql_cursor.fetchone()["count"]
    sql_cursor.execute("SELECT COUNT(*) AS count FROM generated_files WHERE project_id = ?", (project_sql_id,))
    counts["file_associations"] = sql_cursor.fetchone()["count"]
    sql_cursor.execute("SELECT COUNT(*) AS count FROM emails WHERE project_id = ?", (project_sql_id,))
    counts["emails"] = sql_cursor.fetchone()["count"]

    # ask if trully want to delete
    SQL.fetch_and_print(
        sql_cursor,
        "SELECT code AS id, name, description, csv_path, csv_delimiter AS delimiter, csv_multi_delimiter AS multi_delimiter, created_at FROM projects WHERE code = ?",
        (project_id,),
        message="Project to be deleted:",
    )
    counts_message_parts = [f"{name}: {count}" for name, count in counts.items()]
    print(f"These associations with the project will also be deleted:\n{"\n".join(counts_message_parts)}")
    user_input = input(f"Are you sure you want to delete project with id '{project_id}' [y/N]? ").lower()

    if user_input != "y":
        print("Project not deleted.")
        sql_connection.close()
        return

    # delete everything associated and database itself
    sql_cursor.execute("DELETE FROM respondents WHERE project_id = ?", (project_sql_id,))
    sql_cursor.execute("DELETE FROM match_results WHERE project_id = ?", (project_sql_id,))
    sql_cursor.execute("DELETE FROM generated_files WHERE project_id = ?", (project_sql_id,))
    sql_cursor.execute("DELETE FROM emails WHERE project_id = ?", (project_sql_id,))
    sql_cursor.execute("DELETE FROM projects WHERE code = ?", (project_id,))
    sql_connection.commit()
    sql_connection.close()

    print(f"Deleted project '{project_id}' with {", ".join(counts_message_parts)}")


def list_projects():
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    SQL.fetch_and_print(
        sql_cursor,
        "SELECT code AS id, name, description, csv_path, csv_delimiter AS delimiter, csv_multi_delimiter AS multi_delimiter, created_at FROM projects",
        message_not_found="No projects exist.",
    )

    sql_connection.close()


def reset_csv(project_id: str, csv_path: str):
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    # check if a project already exists with this id
    if not SQL.project_exists(sql_cursor, project_id):
        sql_connection.close()
        raise ValueError(f"Project with id '{project_id}' does not exist.")

    # check if csv_path points to a valid file
    csv_exists, csv_hash, csv_size = SQL.get_file_info(csv_path)
    if not csv_exists:
        sql_connection.close()
        raise ValueError(f"Csv data file at '{csv_path}' does not exist.")

    # create project in database
    sql_cursor.execute(
        "UPDATE projects SET csv_path = ?, csv_sha256 = ?, csv_size = ? WHERE id = ?",
        (csv_path, csv_hash, csv_size, project_id),
    )
    sql_connection.commit()

    # print messages
    SQL.fetch_and_print(
        sql_cursor,
        "SELECT code AS id, name, description, csv_path, csv_delimiter AS delimiter, csv_multi_delimiter AS multi_delimiter, created_at FROM projects WHERE code = ?",
        (project_id,),
        message="Project csv updated!",
    )

    # write respondent data
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)
    _, _, respondents = SQL.read_csv_data_file(sql_cursor, project_id)
    for resp in respondents:
        print(resp)
        sql_cursor.execute(
            "UPDATE respondents SET email = ? WHERE id = ? AND project_id = ?",
            (resp.email, resp.id, project_sql_id),
        )
    sql_connection.commit()
    print(f"Wrote {len(respondents)} respondents' data into the database.")

    sql_connection.close()
