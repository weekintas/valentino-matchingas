from matching.match_all import match_all_respondents
from program_input_handling.read_csv_input_data import read_data_from_csv
import utils.sql as SQL


def handle_match(args):
    project_id = args.project_id
    sql_connection = SQL.get_connection()
    sql_cursor = sql_connection.cursor()

    if not SQL.project_exists(sql_cursor, args.project_id):
        sql_connection.close()
        raise ValueError(f"Project with id '{project_id}' does not exist.")

    # check if file exists with correct credentials
    file_exists, message = SQL.data_csv_file_exists(sql_cursor, project_id)
    if not file_exists:
        sql_connection.close()
        raise ValueError(message)

    # get file info
    sql_cursor.execute(
        "SELECT csv_path, csv_delimiter, csv_multi_delimiter FROM projects WHERE code = ?", (project_id,)
    )
    path, delimiter, multi_delimiter = sql_cursor.fetchone()[0:]

    # match respondents
    _, questions_data, respondents = read_data_from_csv(path, delimiter, multi_delimiter, verbose=True)
    match_table = match_all_respondents(respondents, questions_data)

    # check if there are already match results (and ask on overwriting)
    project_sql_id = SQL.get_project_sql_id(sql_cursor, project_id)
    sql_cursor.execute("SELECT COUNT(*) AS count FROM match_results WHERE project_id = ?", (project_sql_id,))
    num_matches = sql_cursor.fetchone()["count"]
    if num_matches > 0:
        user_input = input(
            f"There are already {num_matches} match result database rows. Are you sure you want to override all of those [y/N]? "
        ).lower()
        if user_input != "y":
            sql_connection.close()
            print("Match results not saved.")
            return
        sql_cursor.execute("DELETE FROM match_results WHERE project_id = ?", (project_sql_id,))
        sql_connection.commit()

    # write match results' data
    scores: list[float] = []
    for i in range(len(respondents) - 1):
        for other_resp in respondents[i + 1 :]:
            resp = respondents[i]
            score = match_table.get_compatibility(resp.id, other_resp.id)
            scores.append(score)
            sql_cursor.execute(
                "INSERT INTO match_results (project_id, resp1_id, resp2_id, score) VALUES(?, ?, ?, ?)",
                (project_sql_id, resp.id, other_resp.id, score),
            )
    sql_connection.commit()
    sql_connection.close()
    print(f"Wrote {len(respondents)} respondents' match results.")

    # print statistics
    print(
        f"Top     score: {round(max(scores), 2)}\n"
        f"Lowest  score: {round(min(scores), 2)}\n"
        f"Average score: {round(sum(scores)/len(scores), 2)}"
    )
