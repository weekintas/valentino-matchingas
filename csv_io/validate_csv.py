from pathlib import Path


def check_csv_file_exists(filepath: str) -> bool:
    input_path = Path(filepath)
    return input_path.is_file()
