from enum import Enum


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNSPECIFIED = "UNSPECIFIED"

    @classmethod
    def from_string(cls, value: str) -> "Gender":
        if value is None:
            return cls.UNSPECIFIED

        value = value.strip().upper()

        aliases = {
            "M": cls.MALE,
            "MALE": cls.MALE,
            "MAN": cls.MALE,
            "F": cls.FEMALE,
            "FEMALE": cls.FEMALE,
            "WOMAN": cls.FEMALE,
            "O": cls.OTHER,
            "OTHER": cls.OTHER,
            "UNSPECIFIED": cls.UNSPECIFIED,
            "NONE": cls.UNSPECIFIED,
        }

        try:
            return aliases[value]
        except KeyError:
            raise ValueError(f"Unknown Gender value: '{value}'")

    def __str__(self):
        return self.value
