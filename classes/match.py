from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    respondent_id: int
    compatibility: float


@dataclass(frozen=True)
class MatchGroupParams:
    name: str
    title: str | None
    num_result_to_show: int | None


@dataclass(frozen=True)
class MatchGroup:
    name: str
    title: str | None
    num_result_to_show: int | None
    value: str

    @classmethod
    def from_match_group_params(cls, params: MatchGroupParams, value: str):
        return cls(params.name, params.title, params.num_result_to_show, value)
