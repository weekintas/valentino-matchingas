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

    @classmethod
    def from_database(cls, cursor, project_id: str, num_respondents: int | None = None):
        """If `num_respondents` is specified, will check if all match results are in the database. If not, will raise a `ValueError`"""
        cursor.execute(
            "SELECT * FROM match_results WHERE project_id = (SELECT id FROM projects WHERE code = ?)", (project_id,)
        )

        table = cls()

        num_matches = 0
        for row in cursor:
            table.set_compatibility(row["resp1_id"], row["resp2_id"], row["score"])
            num_matches += 1

        if not num_respondents:
            return table

        expected_num_matches = num_respondents * (num_respondents - 1) // 2
        if num_matches != expected_num_matches:
            raise ValueError(
                f"Number of match rows ({num_matches}) in database does not match expected number for {num_respondents} respondents."
            )

        return table
