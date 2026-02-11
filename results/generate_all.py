from collections import defaultdict
from dataclasses import replace

from utils.classes.match_group import MatchGroup
from utils.classes.match_table import MatchTable
from utils.classes.matchmaking_config import MatchmakingConfig
from utils.classes.respondent import Respondent
from utils.classes.result_file_type import ResultFileType
from results.class_match_group_results import MatchGroupResults, MatchResult
from results.generate_result_file import generate_result_file
from results.result_filepath import get_respondent_result_file_path


def generate_result_files(
    match_groups_data: list[MatchGroup],
    all_respondents: list[Respondent],
    match_table: MatchTable,
    file_types: list[ResultFileType],
    config: MatchmakingConfig,
    verbose: bool = True,
) -> list[tuple[ResultFileType, str, Respondent]]:
    """
    Parameters:
        file_type (str): either `ResultFileType.PDF` or `ResultFileType.EMAIL`, or both in a list
        file_exists_behaviour (str): what to do when file already exists: `"override"`, `"ask"` or `"skip"`
        verbose (bool): should print messages when generating
    """
    # count how many of each file type we generated for printing if verbose
    # (defaultdict so no need to check if f_type exists as key when incrementing)
    generated_file_counts: dict[str, int] = defaultdict(int)
    generated_file_paths: list[tuple[ResultFileType, str, Respondent]] = []

    for respondent in all_respondents:
        match_groups = get_respondent_match_groups_for_template(
            respondent, all_respondents, match_table, match_groups_data
        )
        top_match = get_top_match(match_groups)

        for f_type in file_types:
            filepath = get_respondent_result_file_path(
                respondent,
                config.result_output_dir,
                f_type.get_result_file_extension(),
                config.separate_result_files_by_groups,
            )

            filepath = generate_result_file(
                respondent,
                match_groups,
                top_match,
                filepath,
                f_type,
                config,
                print_generating_message=True,
                print_generated_message=False,
            )
            # if file was successfully generated, add it to the count for display
            if filepath:
                generated_file_counts[f_type] += 1
                generated_file_paths.append((f_type, filepath, respondent))

    if verbose:
        file_type_strings = [f"{f_count} {f_type}" for f_type, f_count in generated_file_counts.items()]
        print(f"Generated {', '.join(file_type_strings)} result files for {len(all_respondents)} respondents!")

    return generated_file_paths


def get_respondent_match_groups_for_template(
    respondent: Respondent,
    all_respondents: list[Respondent],
    match_table: MatchTable,
    match_groups_data: list[MatchGroup],
) -> list[MatchGroupResults]:
    matches_of_wanted_genders = _get_matches_of_wanted_gender(respondent, all_respondents)
    matches_in_match_groups = _get_matches_in_match_groups(respondent, matches_of_wanted_genders)

    unordered_match_groups_for_template: list[tuple[MatchGroup, MatchGroupResults]] = []

    for group_code, matches_in_group in matches_in_match_groups.items():
        # get match group for which to generate
        match_group = next((group for group in match_groups_data if group.code == group_code), None)
        if not match_group:
            raise ValueError(f"Match group with code {group_code} does not exist")

        # if match group is invisible, skip it, since takes no effect in result generating
        if not match_group.get_is_visible(match_groups_data, respondent):
            continue

        match_group_title = match_group.get_title(match_groups_data, respondent)
        match_group_results = _get_match_group_results(
            respondent, match_table, match_groups_data, matches_in_group, match_group
        )

        # if has no results in it and should not be displayed when empty, do not append to the list of match groups
        if not match_group.visible_when_empty and len(match_group_results) == 0:
            continue

        # everything is done, ready to create the object
        unordered_match_groups_for_template.append(
            (match_group, MatchGroupResults(match_group_title, match_group_results))
        )

    # order the groups
    unordered_match_groups_for_template.sort(key=lambda pair: pair[0].order_in_results)
    match_groups_for_template = [pair[1] for pair in unordered_match_groups_for_template]

    return match_groups_for_template


def get_top_match(ordered_match_groups_for_template: list[MatchGroupResults]):
    top_match = None

    for group in ordered_match_groups_for_template:
        # if no results in group, skip it
        if len(group.results) == 0:
            continue
        # if top_match is None, still has not been initialized and we do not need to compare
        if top_match is None:
            top_match = group.results[0]
            continue

        if float(group.results[0].compatibility) > float(top_match.compatibility):
            top_match = group.results[0]

    return top_match


def _get_matches_of_wanted_gender(respondent: Respondent, matches: list[Respondent]) -> list[Respondent]:
    return [match for match in matches if match.gender in respondent.match_genders and match.id != respondent.id]


def _get_matches_in_match_groups(respondent: Respondent, matches: list[Respondent]) -> dict[str, list[Respondent]]:
    """Returns the dict, where keys are codes of groups, values lists of matches in said groups"""
    matches_in_groups: dict[str, list[Respondent]] = {}

    for group_code, value in respondent.groups.items():
        # TODO: Implement NO_RESPONSE
        if value == "NO_RESPONSE":
            continue

        matches_in_groups[group_code] = []
        for match in matches:
            if match.groups.get(group_code) == value:
                matches_in_groups[group_code].append(match)

    return matches_in_groups


def _get_match_group_results(respondent, match_table, match_groups_data, matches_in_group, match_group):
    match_group_results = [
        MatchResult(
            match_group.get_match_fullname(match_groups_data, respondent, match),
            match_group.get_match_description(match_groups_data, respondent, match),
            match_table.get_compatibility(respondent.id, match.id),
        )
        for match in matches_in_group
    ]

    # order the results by compatibility descending
    match_group_results.sort(key=lambda result: result.compatibility, reverse=True)

    # get only X amount of top matches, as dictated by match_group
    #     Note: if num_max_matches_in_group is 'None', it just retrieves all matches from the list
    num_max_matches_in_group = match_group.get_num_results_to_show(match_groups_data, respondent)
    match_group_results = match_group_results[:num_max_matches_in_group]

    # round each compatibility score as dictated by precision param of match_group
    precision = match_group.get_result_precision(match_groups_data, respondent)
    if precision is not None:
        match_group_results = [
            replace(result, compatibility=f"{result.compatibility:.{precision}f}") for result in match_group_results
        ]

    return match_group_results
