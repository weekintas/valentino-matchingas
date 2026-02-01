from typing import Any

from classes.respondent import Respondent
from classes.gender import Gender
from classes.result_file_type import ResultFileType
from utils.jinja import JINJA_ENV
from utils.string import fullname_to_lithuanian_genitive_case, fullname_to_lithuanian_vocative_case


def get_LT_greeting(gender: Gender):
    match gender:
        case Gender.MALE:
            return "Sveikas"
        case Gender.FEMALE:
            return "Sveika"
        case Gender.OTHER | Gender.UNSPECIFIED:
            return "Sveiki"


def get_result_file_html_content(
    file_type: ResultFileType,
    respondent: Respondent,
    match_groups: dict[str, list[dict[str, Any]]],
    top_match: tuple[str, Any],
    relative_template_path: str,
) -> str:
    """
    Arguments:
        top_match (tuple[str, Any]): `top_match[0]` - the name of the top match, `top_match[1]` - compatibility with said match
    """
    template = JINJA_ENV.get_template(relative_template_path)

    result_file_html_content = template.render(
        full_name=(
            fullname_to_lithuanian_vocative_case(respondent.full_name)
            if file_type == ResultFileType.EMAIL
            else fullname_to_lithuanian_genitive_case(respondent.full_name)
        ),
        top_match_name=top_match[0],
        top_match_compatibility=top_match[1],
        match_groups=match_groups,
        greeting=get_LT_greeting(respondent.gender),
        description="Šilalės rajono gimnazijos 2026!",  # only for PDF
        # additional_content_after_recipient_full_name=" iš <strong>2b</strong>",
        footer_content=(
            """
            <div style="font-weight:bold; margin:0; padding:0;">
              Su ❤️ Vykintas Mylimas kartu su Airida Paulauskaite
            </div>
            <div style="margin-top:4px; font-size:12px; line-height:16px;">
              Iškilus klausimams susisiekite <a href="mailto:info@weekintas.lt" style="color:#d6336c;">info@weekintas.lt</a>
            </div>"""
            if file_type == ResultFileType.EMAIL
            else """
            <div style="font-weight:bold; margin:0; padding:0;">
              Su ❤️ Vykintas Mylimas kartu su Airida Paulauskaite
            </div>"""
        ),
    )

    return result_file_html_content
