from utils.constants import ALL_MATCHES_GROUP_CODE


GENERAL_CONFIG = {
    # csv data file config vars
    "CSV_DATA_DELIMITER_CHAR": ",",
    "CSV_DATA_MC_DELIMITER_CHAR": ";",
    # result formatting config vars
    "DEFAULT_RESULT_PRECISION": 0,
    "DEFAULT_NUM_MAX_RESULTS_IN_GROUP": 5,
    # output config vars
    "OUTPUT_DIR": "out",
    "SEPARATE_RESULT_FILES_BY_GROUPS": False,
    "ON_RESULT_FILE_EXISTS_BEHAVIOUR": "override",
    # others:
    "FOOTER_CONTENT_EMAIL": """
        <div style="font-weight:bold; margin:0; padding:0;">
            Su ❤️ Vykintas Mylimas kartu su Airida Paulauskaite
        </div>
        <div style="margin-top:4px; font-size:12px; line-height:16px;">
            Iškilus klausimams susisiekite <a href="mailto:info@weekintas.lt" style="color:#d6336c;">info@weekintas.lt</a>
        </div>""",
    "FOOTER_CONTENT_PDF": """
        <div style="font-weight:bold; margin:0; padding:0;">
            Su ❤️ Vykintas Mylimas kartu su Airida Paulauskaite
        </div>""",
    "PDF_RESULT_FILE_HEADER_DESCRIPTION": "Šilalės rajono gimnazijos 2026!",
}


GROUPS_CONFIG = {
    "klase": {
        "TITLE": "Klasėje:",
        "NUM_RESULTS_TO_SHOW": 5,
        "RESULT_NAMES_FORMAT": lambda groups, resp, match: f"{match.full_name} {match.groups["klase"]}",
        "ORDER_IN_RESULTS": 1,
    },
    "laida": {
        "TITLE": lambda groups, resp: f"Tarp {resp.groups["laida"]}-okų:",
        "NUM_RESULTS_TO_SHOW": 5,
        "RESULT_NAMES_FORMAT": lambda groups, resp, match: f"{match.full_name} {match.groups["klase"]}",
        "ORDER_IN_RESULTS": 2,
    },
    ALL_MATCHES_GROUP_CODE: {
        "TITLE": "Tarp visų Šilalės rajono gimnazijų:",
        "NUM_RESULTS_TO_SHOW": 9,
        # "RESULT_PRECISION": 2,
        "DESCRIPTION": lambda groups, resp, match: f"Mano laida yra: {match.groups["laida"]}",
        "RESULT_NAMES_FORMAT": lambda groups, resp, match: f"{match.full_name} {match.groups["klase"]}",
        # "VISIBLE_IF": lambda this, groups, user: None,
        "VISIBLE_WHEN_EMPTY": True,
        "ORDER_IN_RESULTS": 4,
    },
}
