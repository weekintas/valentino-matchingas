from typing import Any

import pdfkit

from classes.respondent import Respondent
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
    "margin-bottom": "1.5cm",
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
    match_groups: dict[str, list[dict[str, Any]]],
    top_match: tuple[str, Any],
    result_file_path: str,
    file_type: str | None = None,
    file_exists_behaviour: str = "ask",
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
    # validate file_type and get it from file path if neeeded
    file_type = file_type or get_file_extension(result_file_path)
    if file_type not in ("html", "pdf"):
        raise ValueError(f"Incorrect file_type or result_file_path: {file_type}, {result_file_path}")

    if print_generating_message:
        print(f"Generating {file_type} results file: {result_file_path}")

    # get html content of file
    result_file_html_content = get_result_file_html_content(respondent, match_groups, top_match)

    # generate file path and if file already exists, then ask what to do
    should_create_file = make_parent_dirs_for_file(result_file_path, file_exists_behaviour)
    if not should_create_file:
        return None

    # generate file based on its type
    if file_type == "html":
        was_file_generated = _generate_html_result_file(result_file_path, result_file_html_content)
    else:
        was_file_generated = _generate_pdf_result_file(result_file_path, result_file_html_content)

    if print_generated_message and was_file_generated:
        print(f"Generated {file_type} results file: {result_file_path}")

    return result_file_path if was_file_generated else None
