from dataclasses import dataclass

from utils.classes.gender import Gender


@dataclass(frozen=True)
class Respondent:
    """
    Attributes:
        groups (dict[str, str]): Named groups with values that the respondent belongs to, used to display matches in said groups. (For ex. for a student it could be `{"grade": "4", "section": "A"}`, meaning that they are part of class "4A". Then the student would see their top matches in that "section", "grade" and whole pool).
        match_genders (list[Gender]): A list of genders that the respondent will be matched with. In other words, respondent will only see matches of these genders.
        responses (dict[int, int | str | set]): key: question_id, value: response (answer)
    """

    id: int
    full_name: str
    email: str
    groups: dict[str, str]
    gender: Gender
    match_genders: list[Gender]
    responses: dict[int, int | str | set]
    csv_data_row: str | None = None

    def __eq__(self, other: "Respondent"):
        if not isinstance(other, Respondent):
            return NotImplemented
        return self.id == other.id
