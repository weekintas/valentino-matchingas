from utils.classes.respondent import Respondent


def _get_respondent_result_file_filename(respondent: Respondent, extension: str):
    return f"{respondent.full_name} (ID{respondent.id}).{extension}"


def get_respondent_result_file_path(
    respondent: Respondent, base_path: str, extension: str, put_in_group_dir: bool = True
):
    """Generate a filepath (filepath and filemame) in which to put a generated results file for a respondent.
    If `put_in_group_dir` is `True`, then the filepath will be so that the file is in a folder that is named after
    all of the groups the respondent is in combined
    TODO: Give example of put_in_group_dir
    """
    if base_path[-1] != "/":
        base_path += "/"

    filename = _get_respondent_result_file_filename(respondent, extension)
    file_path = base_path
    if put_in_group_dir:
        group_folder_name = " ".join(f"{g_name}-{g_val}" for g_name, g_val in respondent.groups.items())
        file_path += f"{group_folder_name}/"
    file_path += filename
    return file_path
