import csv
from dataclasses import dataclass

from classes.gender import Gender
from classes.match import MatchGroupParams
from classes.question_data import QuestionData, QuestionType
from classes.respondent import Respondent
from utils.constants import (
    CSV_DATA_PARAMETER_DELIMITER,
    PARAM_INDEX_NUM_OPTIONS,
    HEADER_GROUP_PREFIX,
)
from utils.filesystem import file_exists


def _get_group_indexes_from_csv_header(header: list[str]):
    # all of the indexes of group columns and the names + titles of the groups (values)
    group_columns: dict[int, MatchGroupParams] = {}
    for header_i, heading in enumerate(header):
        # if heading is not a group, continue
        if not heading.startswith(HEADER_GROUP_PREFIX):
            continue

        # heading is a GROUP, check if it has a name provided
        group_data = heading.split(CSV_DATA_PARAMETER_DELIMITER)
        if len(group_data) == 1:
            raise ValueError(f"Group heading found but the name of it is not specified (at index {header_i})")

        # group title is also specified if 3 items in total
        group_title = group_data[2] if len(group_data) >= 3 else None
        group_results_to_show = int(group_data[3]) if len(group_data) >= 4 else None

        group_columns[header_i] = MatchGroupParams(group_data[1], group_title, group_results_to_show)

    return group_columns


def _get_question_type_from_heading(item: str) -> QuestionType | None:
    """Returns QuestionType if it exists and is valid, None otherwise"""
    for q_type in QuestionType:
        # headings where a question is specified must start with the question type code
        if item.startswith(q_type.value):
            return q_type
    return None


def _get_question_data_from_csv_header(header: list[str]):
    question_columns: dict[int, QuestionData] = {}

    # loop through all cells in the header and find cells which start with the type's string
    for col_i in range(len(header)):
        heading = header[col_i]
        question_type = _get_question_type_from_heading(heading)
        # if the header is not of question type, skip
        if not question_type:
            continue

        # get num_options as param if it exists
        # all parameters in a heading come after | pipe simbol without spaces (ex. SC|4)
        params = heading.split(CSV_DATA_PARAMETER_DELIMITER)[1:]
        if len(params) == 0:
            # if no params, append the question data and continue
            question_columns[col_i] = QuestionData(col_i, question_type)
            continue

        # if parameters of question found, get them
        # num_options (the amount of options in a question) is always the first argument, if not ommited
        # for ex.: SC|4 specifies a single-choice question with 4 options
        # if in the future more parameters are implemented, one can ommit the num_options param by putting nothing
        # in between the pipe characters (for ex. SC||7 - no num_options specified)
        num_options = params[PARAM_INDEX_NUM_OPTIONS]
        if num_options:
            num_options = int(num_options)

        # all params collected, append the questionData obj
        question_columns[col_i] = QuestionData(col_i, question_type, num_options)

    return question_columns


@dataclass(frozen=True)
class _HeaderIndexes:
    full_name: int
    gender: int | None
    gender_to_match_with: int | None
    match_groups: dict[int, MatchGroupParams]
    question_data_columns: dict[int, QuestionData]


def _process_respondent_csv_data_header(header: list[str]):
    # make all headings be uppercase
    # header = list(map(str.upper, header))

    # get required headings: FULL_NAME
    try:
        full_name_i = header.index("FULL_NAME")
    except ValueError:
        raise ValueError(
            "'FULL_NAME' must be specified in the header of the csv file containing data of the respondents"
        )

    # get optional GENDER and GENDERS_TO_MATCH_WITH
    try:
        gender_i = header.index("GENDER")
        genders_to_match_with_i = header.index("GENDERS_TO_MATCH_WITH")
    except ValueError:
        gender_i = None
        genders_to_match_with_i = None

    # get any GROUP headings (the heading's format is "GROUP|XXX")
    match_groups_i = _get_group_indexes_from_csv_header(header)

    # get the question data
    questions_data_i = _get_question_data_from_csv_header(header)

    return _HeaderIndexes(full_name_i, gender_i, genders_to_match_with_i, match_groups_i, questions_data_i)


def _get_respondent_from_row(row: list[str], row_i: int, h_indexes: _HeaderIndexes, multi_delimiter: str):
    try:
        # full name
        full_name = row[h_indexes.full_name]

        # gender (if specified is added, if not then matching without gender selections)
        if h_indexes.gender is not None:
            gender = Gender.from_string(row[h_indexes.gender])
            gender_strs_to_match_with = row[h_indexes.gender_to_match_with].split(multi_delimiter)
            genders_to_match_with = [Gender.from_string(gs) for gs in gender_strs_to_match_with]
        else:
            gender = Gender.UNSPECIFIED
            genders_to_match_with = [Gender.UNSPECIFIED]

        # groups
        groups: dict[str, str] = {}
        for group_i, group_params in h_indexes.match_groups.items():
            groups[group_params] = row[group_i]

        # responses to questions
        responses = {}
        for question_i, question_data in h_indexes.question_data_columns.items():
            ans = row[question_i]
            ans_type = question_data.get_expected_answer_type()
            # if answer type is int or set, try to convert it
            if ans_type is int:
                ans = int(ans)
            elif ans_type is set:
                ans = set(ans.split(multi_delimiter))
            elif ans_type is not str:
                raise ValueError()
            responses[question_data.id] = ans

    except IndexError:
        raise ValueError(
            f"Respondent data row (at index: {row_i}) is incorrectly formatted (does not match the csv header)."
        )
    except Exception as e:
        raise ValueError(f"Respondent data row (at index: {row_i}) is incorrectly formatted: {e}")

    # create respondent
    return Respondent(row_i, full_name, groups, gender, genders_to_match_with, responses)


def read_data_from_csv(
    file_name: str, delimiter: str, multi_delimiter: str, verbose: bool = True
) -> tuple[list[QuestionData], dict[int, Respondent]]:
    """
    Returns a tuple with two items:
        `list[QuestionData]`: a list with all questions' data
        `dict[int, Respondent]`: a dictionary with all respondent ids and respondents themselves (not a `list[Respondent]`, because program often looks up respondents by their id and it is way more simple and faster to have this as a dictionary rather than a list)
    """
    if verbose:
        print(f"Reading input csv file: {file_name}...")

    # check if the file exists
    if not file_exists(file_name):
        raise FileNotFoundError(f"The csv input file {file_name} does not exist")

    questions_data: list[QuestionData] = []
    respondent_dict: dict[int, Respondent] = {}

    with open(file_name, "r", encoding="UTF-8", newline="") as file:
        csv_reader = csv.reader(file, delimiter=delimiter, skipinitialspace=True, quoting=csv.QUOTE_ALL)
        # get all of the info from the header
        header = next(csv_reader)
        h_indexes = _process_respondent_csv_data_header(header)  # indexes where particular data is in the header
        questions_data = list(h_indexes.question_data_columns.values())
        # process each respondent and use row index as the respondent's id
        for row_i, row in enumerate(csv_reader):
            respondent = _get_respondent_from_row(row, row_i, h_indexes, multi_delimiter)
            respondent_dict[row_i] = respondent

    if verbose:
        print(f"Successfully read data of {len(questions_data)} questions and {len(respondent_dict)} respondents!\n")

    return questions_data, respondent_dict
