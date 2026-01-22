from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    respondent_id: int
    compatibility: float


@dataclass(frozen=True)
class MatchGroup:
    name: str
    value: str
