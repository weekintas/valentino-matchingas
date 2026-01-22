import os
from pathlib import Path


def file_exists(filepath: str) -> bool:
    input_path = Path(filepath)
    return input_path.is_file()


def get_file_extension(filepath: str) -> str:
    if not filepath:
        raise ValueError("Filepath is empty")

    filename, extension = os.path.splitext(filepath)
    if not extension:
        raise ValueError(f"No file extension found in '{filepath}'")

    return extension.lstrip(".").lower()


def make_parent_dirs_for_file(
    filepath: str,
    if_exists_behaviour: str,
) -> bool:
    """
    Parameters:
        if_exists_behaviour (str): what to do when file already exists: `"override"`, `"ask"` or `"skip"`
    Returns:
        bool: whether the file should be created or not
    """
    if_exists_behaviour = if_exists_behaviour.lower()

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        if if_exists_behaviour == "override":
            print(f"File '{filepath}' already exists. Overriding...")
            return True
        if if_exists_behaviour == "skip":
            print(f"File '{filepath}' already exists. Skipping...")
            return False

        # if should ask, ask
        response = input(f"File '{filepath}' already exists. Override it? [Y/n]: ")
        if response.lower() == "n":
            print("Skipping this file's generation")
            return False
        return True
    return True
