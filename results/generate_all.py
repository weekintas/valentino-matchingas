from itertools import chain
from collections import defaultdict

from classes.match import Match, MatchGroup
from classes.match_table import MatchTable
from classes.respondent import Respondent
from matching.get_grouped_matches import (
    get_respondent_matches_of_wanted_genders,
    get_respondent_matches_in_groups,
)
from results.generate_result_file import generate_result_file
from results.result_filepath import get_respondent_result_file_path
from utils.constants import ALL_PARTICIPANTS_GROUP_TITLE


def _normalize_file_type_arg(file_type: str | list[str]) -> list[str]:
    """Turn file_type into a lowercase list of file types"""
    if isinstance(file_type, str):
        return [file_type.lower()]
    # check if is list and all items in the list are strings
    elif isinstance(file_type, list) and all(isinstance(ft, str) for ft in file_type):
        return [ft.lower() for ft in file_type]
    else:
        raise ValueError(f"Incorrect argument 'file_type' type: {type(file_type)}")


def _get_group_title_for_display(group: MatchGroup | None):
    if group:
        return f'Among those in {group.name.lower()} "{group.value}"'

    # if `group` is `None`, then return the default name for the whole respondent pool
    return ALL_PARTICIPANTS_GROUP_TITLE


def _build_match_groups_for_display_data(
    matches_in_groups: dict[MatchGroup, list[Match]],
    all_matches: list[Match],
    respondent_dict: dict[int, Respondent],
    max_num_of_results_in_group: int | None,
) -> dict[str, list[dict[str, float]]]:
    if len(all_matches) == 0:
        return {}

    group_matches: dict[str, list[dict[str, float]]] = {}

    # add all matches as a group as well, because it is not a particular group, but need to be displayed as one
    for match_group, matches in chain(matches_in_groups.items(), [(None, all_matches)]):
        # if no matches in one group, we do not display it at all
        if len(matches) == 0:
            continue
        # if max amount of matches specified, limit the amount
        if max_num_of_results_in_group:
            matches = matches[:max_num_of_results_in_group]

        group_title = _get_group_title_for_display(match_group)
        group_matches[group_title] = []

        for match in matches:
            group_matches[group_title].append(
                {"name": respondent_dict[match.respondent_id].full_name, "compatibility": match.compatibility}
            )

    return group_matches


def _format_compatibilities_for_display(
    group_matches: dict[str, list[dict[str, float]]], precision: int | None
) -> dict[str, list[dict[str, str]]]:
    """Formats all of the compatibility numbers in the group_matches so they appear in the document to the amount of
    decimal places they should. If `precision` is `None`, then do not round at all"""
    formatted_group_matches: dict[str, list[dict[str, str]]] = {}

    for g_name, g_matches in group_matches.items():
        formatted_group_matches[g_name] = []
        for match in g_matches:
            name = match["name"]
            compatibility = match["compatibility"]
            if precision is None or precision < 0:
                compatibility = str(compatibility)
            else:
                compatibility = f"{compatibility:.{precision}f}"
            formatted_group_matches[g_name].append({"name": name, "compatibility": compatibility})

    return formatted_group_matches


def _prepare_match_groups_for_respondent(
    respondent: Respondent,
    respondent_dict: dict[int, Respondent],
    match_table: MatchTable,
    max_num_of_results_in_group: int | None,
    precision: int | None,
) -> dict[str, list[dict[str, str]]]:
    # get all matches for the respondent which are only of genders the respondent wishes
    all_matches = get_respondent_matches_of_wanted_genders(respondent, respondent_dict, match_table)
    # get matches separated (and filtered) into match_groups that the respondent is in
    matches_in_groups = get_respondent_matches_in_groups(respondent, respondent_dict, all_matches)
    # makes match_groups var which contains more accessible match data in groups for jinja to use
    match_groups = _build_match_groups_for_display_data(
        matches_in_groups, all_matches, respondent_dict, max_num_of_results_in_group
    )
    # finally, format compatibilities (as of right now it only formats them as string with specified precision)
    match_groups = _format_compatibilities_for_display(match_groups, precision)

    return match_groups


def generate_result_files(
    match_table: MatchTable,
    respondent_dict: dict[int, Respondent],
    file_type: str | list[str],
    precision: int | None,
    max_num_of_results_in_group: int | None,
    output_dir: str = f"_output/result_files/",
    separate_into_group_dirs: bool = True,
    file_exists_behaviour="ask",
    verbose: bool = True,
) -> None:
    """
    Parameters:
        file_type (str): either `"html"` or `"pdf"`, or both in a list: `["html", "pdf"]`
        file_exists_behaviour (str): what to do when file already exists: `"override"`, `"ask"` or `"skip"`
        verbose (bool): should print messages when generating
    """
    file_types = _normalize_file_type_arg(file_type)
    # count how many of each file type we generated for printing if verbose
    # (defaultdict so no need to check if f_type exists as key when incrementing)
    generated_file_counts: dict[str, int] = defaultdict(int)

    for respondent in respondent_dict.values():
        match_groups = _prepare_match_groups_for_respondent(
            respondent, respondent_dict, match_table, max_num_of_results_in_group, precision
        )

        # top_matches is ordered by compatibility descending, and top match is in the whole pool
        top_match = match_groups[ALL_PARTICIPANTS_GROUP_TITLE][0]

        for f_type in file_types:
            # f_type (type of file) is always the same as the extension
            filepath = get_respondent_result_file_path(respondent, output_dir, f_type, separate_into_group_dirs)

            was_file_generated = generate_result_file(
                respondent,
                match_groups,
                (top_match["name"], top_match["compatibility"]),
                filepath,
                f_type,
                file_exists_behaviour,
                print_generating_message=True,
                print_generated_message=False,
            )
            # if file was successfully generated, add it to the count for display
            if was_file_generated:
                generated_file_counts[f_type] += 1

    if verbose:
        file_type_strings = [f"{f_count} {f_type}" for f_type, f_count in generated_file_counts.items()]
        print(f"Generated {', '.join(file_type_strings)} result files for {len(respondent_dict)} respondents!")
