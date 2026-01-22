from typing import Any

from classes.respondent import Respondent
from utils.jinja import JINJA_ENV


def get_result_file_html_content(
    respondent: Respondent,
    match_groups: dict[str, list[dict[str, Any]]],
    top_match: tuple[str, Any],
) -> str:
    """
    Arguments:
        top_match (tuple[str, Any]): `top_match[0]` - the name of the top match, `top_match[1]` - compatibility with said match
    """
    template = JINJA_ENV.get_template("respondent_results.html")

    result_file_html_content = template.render(
        full_name=respondent.full_name,
        top_match_name=top_match[0],
        top_match_compatibility=top_match[1],
        match_groups=match_groups,
    )

    return result_file_html_content
