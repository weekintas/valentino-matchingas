class MatchTable:
    """Stores compatibilities between respondents using a symmetric 2d dictionary."""

    def __init__(self):
        self._table: dict[int, dict[int, float]] = {}

    def set_compatibility(self, resp1_id: int, resp2_id: int, compatibility: float):
        # store the results symmetrically in the table, so we store the compatibility two times
        if resp1_id not in self._table:
            self._table[resp1_id] = {resp2_id: compatibility}
        else:
            self._table[resp1_id][resp2_id] = compatibility

        if resp2_id not in self._table:
            self._table[resp2_id] = {resp1_id: compatibility}
        else:
            self._table[resp2_id][resp1_id] = compatibility

    def get_respondent_compatibilities(self, resp_id: int):
        return {id: compatibility for id, compatibility in self._table[resp_id].items() if id != resp_id}
