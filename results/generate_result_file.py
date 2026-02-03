from typing import Any

import pdfkit

from classes.matchmaking_config import MatchmakingConfig
from classes.respondent import Respondent
from classes.result_file_type import ResultFileType
from results.class_match_group_results import MatchGroupResults, MatchResult
from results.generate_html_content import get_result_file_html_content
from utils.filesystem import make_parent_dirs_for_file, get_file_extension


def _generate_html_result_file(result_file_path: str, file_html_content: str) -> bool:
    """Returns bool whether file generation succeeded"""
    try:
        with open(result_file_path, "w", encoding="UTF-8") as html_file:
            html_file.write(file_html_content)
    except OSError as e:
        print(f"Failed to generate html results file '{result_file_path}': {e}")
        return False

    return True


_PDFKIT_OPTIONS = {
    "encoding": "UTF-8",
    "margin-top": "1cm",
    "margin-right": "1cm",
    "margin-bottom": "1cm",
    "margin-left": "1cm",
}


def _generate_pdf_result_file(result_file_path: str, file_html_content: str) -> bool:
    """Returns bool whether file generation succeeded"""
    try:
        pdfkit.from_string(file_html_content, result_file_path, options=_PDFKIT_OPTIONS)
    except Exception as e:
        print(f"Failed to generate pdf results file '{result_file_path}': {e}")
        return False

    return True


def generate_result_file(
    respondent: Respondent,
    match_groups: list[MatchGroupResults],
    top_match: MatchResult,
    result_file_path: str,
    file_type: ResultFileType,
    config: MatchmakingConfig,
    print_generating_message: bool = True,
    print_generated_message: bool = True,
) -> str | None:
    """
    Parameters:
        top_match (tuple[str, Any]): `top_match[0]` - the name of the top match, `top_match[1]` - compatibility with said match
        file_type (str | None): either 'html' or 'pdf'. If `None`, then determines file type by extension of the
            `result_file_path`
        file_exists_behaviour (str): what to do when file already exists: `"override"`, `"ask"` or `"skip"`
    Returns:
        str | None: filepath of the file generated, if not generated - `None`
    """

    if print_generating_message:
        print(f"Generating {file_type} results file: {result_file_path}")

    # get html content of file
    result_file_html_content = get_result_file_html_content(
        file_type, respondent, match_groups, top_match, config, file_type.get_result_file_path()
    )

    # generate file path and if file already exists, then ask what to do
    should_create_file = make_parent_dirs_for_file(result_file_path, config.on_result_file_exists_behaviour)
    if not should_create_file:
        return None

    # generate file based on its type
    result_file_extension = file_type.get_result_file_extension().lower()
    if result_file_extension == "html":
        was_file_generated = _generate_html_result_file(result_file_path, result_file_html_content)
    elif result_file_extension == "pdf":
        was_file_generated = _generate_pdf_result_file(result_file_path, result_file_html_content)
    else:
        raise ValueError(f"Invalid file_type result file extension: {result_file_extension}")

    if print_generated_message and was_file_generated:
        print(f"Generated {file_type} results file: {result_file_path}")

    return result_file_path if was_file_generated else None
