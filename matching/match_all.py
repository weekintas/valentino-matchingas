from classes.match_table import MatchTable
from classes.question_data import QuestionData, QuestionType
from classes.respondent import Respondent


def _calc_points_yn_or_sc(r1, r2, qd: QuestionData):
    # if answers match, get all points, if not: 0 points
    return qd.max_points if r1 == r2 else 0


def _calc_points_mc(r1, r2, qd: QuestionData):
    # divide the amount of matching answers by the amount of total answers chosen
    num_of_matching_answers = len(r1 & r2)
    num_of_answers_chosen = len(r1 | r2)
    return num_of_matching_answers / num_of_answers_chosen * qd.max_points


def _calc_points_rating(r1, r2, qd: QuestionData):
    difference = abs(r1 - r2)
    num_options = qd.num_options
    # points would be calculated by (num_options - difference) / (num_options) * max_points,
    # but difference can only be between 0 and num_options - 1.
    # So, to make it so respondents get 0 points when their chosen ratings differ at biggest possible
    # value, we use difference - 1
    return (num_options - difference - 1) / (num_options - 1) * qd.max_points


def _calculate_points_for_response(response1, response2, question_data: QuestionData) -> float:
    """
    Calculates the amount of points (between `0` and `question_data.max_points` inclusive) that both respondents receive
    for this question.
    """

    # calculate points based on type
    match question_data.question_type:
        case QuestionType.YES_NO | QuestionType.SINGLE_CHOICE:
            return _calc_points_yn_or_sc(response1, response2, question_data)
        case QuestionType.MULTIPLE_CHOICE:
            return _calc_points_mc(response1, response2, question_data)
        case QuestionType.RATING:
            return _calc_points_rating(response1, response2, question_data)


def _match_2_respondents(respondent1: Respondent, respondent2: Respondent, questions_data: list[QuestionData]) -> float:
    """
    Get the compatibility between two respondents, with `precision` if not `None`.
    Returns compatibility as a percentage (meaning range 0-100)
    """
    # we calculate the percentage by getting the sum of points for each response, and then dividing by the total
    # possible amount of points
    points = 0.0
    max_points = 0.0
    for question_id, response1 in respondent1.responses.items():
        try:
            response2 = respondent2.responses[question_id]
        except KeyError:
            raise ValueError("Two respondents do not have responses to the same question")

        try:
            # get the question_data
            # First we get a list of all question datas with matching ids (meaning we get a list of either 1 or 0 question_data instances)
            # Then we get the first (and only if exists) question_data instance using next
            # If list is empty (meaning one respondent does not have an answer to the question), next raises an error
            question_data = next(q_data for q_data in questions_data if q_data.id == question_id)
        except StopIteration:
            raise ValueError("Respondent has a response to a question whose id does not exist")

        points += _calculate_points_for_response(response1, response2, question_data)
        max_points += question_data.max_points

    # if max points is somehow 0, can not divide by 0 and thus match is also 0%
    if max_points == 0.0:
        return 0

    # else calculate compatibility as percentage and round if necassary
    compatibility = points / max_points * 100
    return compatibility


def match_all_respondents(
    respondents: list[Respondent], questions_data: list[QuestionData], verbose: bool = True
) -> MatchTable:
    match_table = MatchTable()

    if verbose:
        print(f"Matching {len(respondents)} respondents...")

    # we only need to match to the respondents in the list that are upcoming in the list compared to this respondent,
    # since this respondent will already be matched with those that are behind
    for i, respondent1 in enumerate(respondents):
        for respondent2 in respondents[i + 1 :]:
            compatibility = _match_2_respondents(respondent1, respondent2, questions_data)
            match_table.set_compatibility(respondent1.id, respondent2.id, compatibility)

    if verbose:
        print(f"Successfully matched {len(respondents)}!\n")

    return match_table
