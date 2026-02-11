from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from utils.classes.respondent import Respondent


_MatchGroupGeneralCallable: TypeAlias = Callable[[list["MatchGroup"], "Respondent"], Any]
_MatchGroupSpecificMatchCallable: TypeAlias = Callable[[list["MatchGroup"], "Respondent", "Respondent"], Any]


@dataclass(frozen=True)
class MatchGroup:
    """
    :param code: the code identifier for this group across all configs and matching systems
    :type code: str
    :param value: the value entered by the respondent. Is only `None` when the respondent has entered no value for it
    :type value: str
    :param title: the title to display in result sent for this group as the heading. If `None`, `code` is used
    :type title: str | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], str] | None
    :param num_results_to_show: amount of results to show. If `None`, defaults to one set in the program via cli
    :type num_results_to_show: int | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], int] | None
    :param result_precision: to what decimal places round the percentage results in this group. If `None`, defaults to one set in the program via cli.
    :type result_precision: int | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], int] | None
    :param match_description: Text to show in smaller gray text under each match'es full name. If `None` - will not show at all.
    :type match_description: str | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], str] | None
    :param match_fullname_formatter: What full name to display of each match in this group. If `None` - displays `Respondent.full_name`
    :type match_fullname_formatter: str | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], str] | None
    :param visible_if: whether this group is shown in respondent's results. If `None` defaults to `True`
    :type visible_if: bool | Callable[["MatchGroup", list["MatchGroup"], "Respondent"], bool] | None
    :param visible_when_empty: if there are now results in this group, should it be displayed? Default `False`
    :type visible_when_empty: bool
    :param order_in_results: the order of which this group should appear in respondent's results starting from top, from 1
    :type order_in_results: int
    """

    code: str
    title: str | _MatchGroupGeneralCallable | None = None
    num_results_to_show: int | _MatchGroupGeneralCallable | None = None
    result_precision: int | _MatchGroupGeneralCallable | None = None
    match_description: str | _MatchGroupSpecificMatchCallable | None = None
    match_fullname_formatter: str | _MatchGroupSpecificMatchCallable | None = None
    visible_if: bool | _MatchGroupGeneralCallable | None = True
    visible_when_empty: bool = False
    order_in_results: int = -1

    def get_title(self, groups: list["MatchGroup"], resp: "Respondent") -> str:
        if self.title is None:
            return self.code
        if isinstance(self.title, str):
            return self.title
        if callable(self.title):
            return self.title(groups, resp)
        raise TypeError(
            f"'MatchGroup.title' is of wrong type ({type(self.title)}). Must be on of: 'str', '_MatchGroupGeneralCallable', 'None'"
        )

    def get_num_results_to_show(self, groups: list["MatchGroup"], resp: "Respondent") -> int | None:
        if self.num_results_to_show is None or isinstance(self.num_results_to_show, int):
            return self.num_results_to_show
        if callable(self.num_results_to_show):
            return self.num_results_to_show(groups, resp)
        raise TypeError(
            f"'MatchGroup.num_results_to_show' is of wrong type ({type(self.num_results_to_show)}). Must be on of: 'int', '_MatchGroupGeneralCallable', 'None'"
        )

    def get_result_precision(self, groups: list["MatchGroup"], resp: "Respondent") -> int | None:
        if self.result_precision is None or isinstance(self.num_results_to_show, int):
            return self.result_precision
        if callable(self.result_precision):
            return self.result_precision(groups, resp)
        raise TypeError(
            f"'MatchGroup.result_precision' is of wrong type ({type(self.result_precision)}). Must be on of: 'int', '_MatchGroupGeneralCallable', 'None'"
        )

    def get_match_description(self, groups: list["MatchGroup"], resp: "Respondent", match: "Respondent") -> str | None:
        if self.match_description is None or isinstance(self.match_description, str):
            return self.match_description
        if callable(self.match_description):
            return self.match_description(groups, resp, match)
        raise TypeError(
            f"'MatchGroup.match_description' is of wrong type ({type(self.match_description)}). Must be on of: 'str', '_MatchGroupSpecificMatchCallable', 'None'"
        )

    def get_match_fullname(self, groups: list["MatchGroup"], resp: "Respondent", match: "Respondent") -> str:
        if self.match_fullname_formatter is None:
            return match.full_name
        if isinstance(self.match_fullname_formatter, str):
            return self.match_fullname_formatter
        if callable(self.match_fullname_formatter):
            return self.match_fullname_formatter(groups, resp, match)
        raise TypeError(
            f"'MatchGroup.match_fullname_formatter' is of wrong type ({type(self.match_fullname_formatter)}). Must be on of: 'str', '_MatchGroupSpecificMatchCallable', 'None'"
        )

    def get_is_visible(self, groups: list["MatchGroup"], resp: "Respondent") -> bool:
        if self.visible_if is None:
            return True
        if isinstance(self.visible_if, bool):
            return self.visible_if
        if callable(self.visible_if):
            return self.visible_if(groups, resp)
        raise TypeError(
            f"'MatchGroup.visible_if' is of wrong type ({type(self.visible_if)}). Must be on of: 'bool', '_MatchGroupGeneralCallable', 'None'"
        )
