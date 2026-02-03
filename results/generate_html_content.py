from classes.matchmaking_config import MatchmakingConfig
from classes.respondent import Respondent
from classes.gender import Gender
from classes.result_file_type import ResultFileType
from results.class_match_group_results import MatchGroupResults, MatchResult
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
    match_groups: list[MatchGroupResults],
    top_match: MatchResult,
    config: MatchmakingConfig,
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
        top_match=top_match,
        match_groups=match_groups,
        greeting=get_LT_greeting(respondent.gender),
        description=config.pdf_result_file_header_description,
        footer_content=(
            config.footer_content_email if file_type == ResultFileType.EMAIL else config.footer_content_pdf
        ),
    )

    return result_file_html_content
