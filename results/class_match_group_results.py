from dataclasses import dataclass


@dataclass(frozen=True)
class MatchGroupResults:
    title: str
    results: list["MatchResult"]


@dataclass(frozen=True)
class MatchResult:
    full_name: str
    description: str | None
    compatibility: float | str
    # is_top_match: bool
