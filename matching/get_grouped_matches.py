from classes.match import Match, MatchGroup
from classes.match_table import MatchTable
from classes.respondent import Respondent


def get_respondent_matches_of_wanted_genders(
    respondent: Respondent, respondent_dict: dict[int, Respondent], match_table: MatchTable
) -> list[Match]:
    """returns list of Match sorted by compatibility descending. Only matches of respondent's wanted genders are returned"""
    gender_filtered_matches = [
        Match(match_id, compatibility)
        for match_id, compatibility in match_table.get_respondent_compatibilities(respondent.id).items()
        if respondent_dict[match_id].gender in respondent.match_genders
    ]

    # Order by compatibility descending
    gender_filtered_matches.sort(key=lambda x: x.compatibility, reverse=True)

    return gender_filtered_matches


def get_respondent_matches_in_groups(
    respondent: Respondent, respondent_dict: dict[int, Respondent], matches: list[Match]
) -> dict[MatchGroup, list[Match]]:
    """Returns a list of MatchGroup objects, where in each group there is a maximum of `match_amount_per_group` amount of top matches."""
    # init empty list of MatchGroups
    matches_in_groups: dict[MatchGroup, list[Match]] = {
        MatchGroup.from_match_group_params(group_params, group_val): []
        for group_params, group_val in respondent.groups.items()
    }

    for candidate_match in matches:
        # check if the respondent and the match belong to any shared groups together - if so, add the match to all
        # such groups (the group name and value both have to be equal)
        candidate_respondent = respondent_dict[candidate_match.respondent_id]
        for group_params, group_value in respondent.groups.items():
            if candidate_respondent.groups.get(group_params) == group_value:
                matches_in_groups[MatchGroup.from_match_group_params(group_params, group_value)].append(
                    Match(candidate_respondent.id, candidate_match.compatibility)
                )

    return matches_in_groups
