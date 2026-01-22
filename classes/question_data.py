from dataclasses import dataclass
from enum import Enum


class QuestionType(Enum):
    YES_NO = "YN"
    SINGLE_CHOICE = "SC"
    MULTIPLE_CHOICE = "MC"
    RATING = "RT"


@dataclass(frozen=True)
class QuestionTypeWeights:
    """
    Attributes:
        base_weight (float): question's base weight, always added to it as is
        option_amount_weight (float): weight that is tied to the amount of options of a question. A weight to the
            question is added when doing `option_amount_weight * num_options`
    """

    base_weight: float
    option_amount_weight: float


_QUESTION_TYPE_WEIGHTS = {
    QuestionType.YES_NO: QuestionTypeWeights(2.0, 0.0),
    QuestionType.SINGLE_CHOICE: QuestionTypeWeights(2.0, 0.5),
    QuestionType.MULTIPLE_CHOICE: QuestionTypeWeights(3.0, 0.4),
    QuestionType.RATING: QuestionTypeWeights(2.5, 0.5),
}


class QuestionData:
    def __init__(self, id: int, question_type: QuestionType, num_options: int | None = None):
        self.id = id
        self.question_type = question_type

        if question_type == QuestionType.YES_NO:
            self.num_options = 2
        # default num_options if not specified is 5
        elif question_type == QuestionType.RATING:
            self.num_options = num_options if num_options else 5
        # if question_type is not of YES_NO or RATING, num_options must be specified and greater than 0
        elif num_options:
            self.num_options = num_options
        else:
            raise TypeError(
                f"num_options not specified when initialising QuestionData object with question_type {question_type}"
            )

        # once we have num_options, can init the max_points
        question_weights = _QUESTION_TYPE_WEIGHTS[question_type]
        self.max_points = question_weights.base_weight + question_weights.option_amount_weight * self.num_options

    def __eq__(self, other: "QuestionData"):
        if not isinstance(other, QuestionData):
            return NotImplemented
        return self.id == other.id

    def get_expected_answer_type(self):
        """Return the type of which the answer (response) to this question should be"""
        match self.question_type:
            case QuestionType.RATING:
                return int
            case QuestionType.MULTIPLE_CHOICE:
                return set
            case _:
                return str
