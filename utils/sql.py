import sqlite3
import tabulate
import os
import hashlib

from program_input_handling.read_csv_input_data import read_data_from_csv
from utils.constants import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def project_exists(cursor, project_id: str):
    cursor.execute("SELECT COUNT(*) AS count FROM projects WHERE code = ?", (project_id,))
    project_count = cursor.fetchone()["count"]
    return project_count != 0


def get_project_sql_id(cursor, project_id: str):
    if not project_exists(cursor, project_id):
        raise ValueError(f"Project with id '{project_id}' does not exist.")
    cursor.execute("SELECT id FROM projects WHERE code = ?", (project_id,))
    return cursor.fetchone()["id"]


def fetch_and_print(
    cursor, query: str, params: tuple = (), message: str | None = None, message_not_found: str | None = None
):
    """
    Executes a SQL query and prints the result as a nice table.

    Args:
        cursor: sqlite3 cursor
        query: SQL SELECT query with ? placeholders
        params: tuple of parameters to safely substitute
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print(message_not_found or "No rows found in data table.")
        return

    # get column names from cursor description
    columns = [desc[0] for desc in cursor.description]

    # convert each row tuple to dict for tabulate
    dict_rows = [dict(zip(columns, row)) for row in rows]
    if message:
        print(message)
    print(tabulate.tabulate(dict_rows, headers="keys", tablefmt="grid"))


def get_file_info(path: str):
    """
    Returns (exists, sha256, size) for a file.
    - exists: bool
    - sha256: hex string or None if file doesn't exist
    - size: int bytes or None if file doesn't exist
    """
    if not os.path.isfile(path):
        return False, None, None

    # get size
    size = os.path.getsize(path)

    # compute SHA256
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return True, sha256_hash.hexdigest(), size


def data_csv_file_exists(cursor, project_id: str) -> tuple[bool, str | None]:
    if not project_exists(cursor, project_id):
        raise ValueError(f"Project with id '{project_id}' does not exist.")

    cursor.execute("SELECT csv_path, csv_sha256, csv_size FROM projects WHERE code = ?", (project_id,))
    path, expected_hash, expected_size = cursor.fetchone()[0:]

    file_exists, file_hash, file_size = get_file_info(path)
    if not file_exists:
        return (
            False,
            f"Csv data file at '{path}' does not exist. Ensure to move it to this location or run 'project set_csv <project_id> <csv_path>' to bind a new csv data file.",
        )

    if file_hash != expected_hash:
        return (
            False,
            f"Csv data file at '{path}' has an incorrect file hash. Ensure the file has not been modified or run 'project set_csv <project_id> <csv_path>' to re-bind the csv data file.",
        )
    if file_size != expected_size:
        return (
            False,
            f"Csv data file at '{path}' has a different size than expected. Ensure the file has not been modified or run 'project set_csv <project_id> <csv_path>' to re-bind the csv data file.",
        )

    return True, None


def read_csv_data_file(cursor, project_id: str):
    cursor.execute("SELECT csv_path, csv_delimiter, csv_multi_delimiter FROM projects WHERE code = ?", (project_id,))
    path, delimiter, multi_delimiter = cursor.fetchone()[0:]
    return read_data_from_csv(path, delimiter, multi_delimiter, verbose=True)
