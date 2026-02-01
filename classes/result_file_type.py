from enum import Enum

from utils.constants import EMAIL_TEMPLATE_RELATIVE_PATH, PDF_RESULTS_TEMPLATE_RELATIVE_PATH


class ResultFileType(Enum):
    PDF = "pdf"
    EMAIL = "email"

    @classmethod
    def from_string(cls, value: str):
        if value is None:
            return None

        value = value.strip().lower()

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"Invalid ResultFileType: {value}")

    def __str__(self):
        return self.value

    def get_result_file_path(self):
        match self:
            case ResultFileType.PDF:
                return PDF_RESULTS_TEMPLATE_RELATIVE_PATH
            case ResultFileType.EMAIL:
                return EMAIL_TEMPLATE_RELATIVE_PATH

    def get_result_file_extension(self):
        match self:
            case ResultFileType.PDF:
                return "pdf"
            case ResultFileType.EMAIL:
                return "html"
