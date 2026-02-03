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

    def get_compatibility(self, resp1_id: int, resp2_id: int):
        resp1_compatibilities = self.get_respondent_compatibilities(resp1_id)
        compatibility = resp1_compatibilities.get(resp2_id, None)
        if compatibility:
            return compatibility

        raise ValueError(f"No compatibility in 'MatchTable' between respondents with ids '{resp1_id}' and '{resp2_id}'")
