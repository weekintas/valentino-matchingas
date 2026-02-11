from pathlib import Path
import importlib.util as implib
from types import ModuleType

from utils.classes.match_group import MatchGroup
from utils.classes.matchmaking_config import MatchmakingConfig
from utils.constants import ALL_MATCHES_GROUP_CODE


def process_py_config_file(
    path: str | None, cli_config: MatchmakingConfig, group_codes: list[str]
) -> tuple[MatchmakingConfig, list[MatchGroup]]:
    # make sure group codes includes the all matches code
    group_codes = [*group_codes, ALL_MATCHES_GROUP_CODE]

    if path is None:
        print(f"Python configuration file not given. Using values from cli arguments and/or default values...")
        return cli_config, _init_match_groups_from_cli_args(cli_config, group_codes)
    else:
        print(f"Processing python configuration file: {path}...")

    file_is_valid = _check_path_validity(path)
    if not file_is_valid:
        print("Using values from cli arguments and/or default values...")
        return cli_config, _init_match_groups_from_cli_args(cli_config, group_codes)

    module = _get_module(path)

    if _check_if_has_attr(module, "GENERAL_CONFIG"):
        general_config = _get_general_config_from_file(module, cli_config)
    else:
        general_config = cli_config

    if _check_if_has_attr(module, "GROUPS_CONFIG"):
        groups_config = _get_groups_config_from_file(module, group_codes, cli_config)
    else:
        groups_config = _init_match_groups_from_cli_args(general_config, group_codes)

    return general_config, groups_config


def _init_match_groups_from_cli_args(cli_config: MatchmakingConfig, group_codes: list[str]):
    return [
        MatchGroup(
            code,
            num_results_to_show=cli_config.default_num_max_results_in_group,
            result_precision=cli_config.default_result_precision,
        )
        for code in group_codes
    ]


def _check_path_validity(path: str):
    path = Path(path)

    if not path.exists():
        print(f"Config file not found: {path}")
        return False

    if not path.is_file():
        print(f"Config path is not a file: {path}")
        return False

    if path.suffix != ".py":
        print(f"Config must be a .py file, got: {path}")
        return False

    return True


def _get_module(path: str):
    spec = implib.spec_from_file_location("matchmaker_config_file", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"INTERNAL ERROR: Cannot load module from {path}")

    module = implib.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _check_if_has_attr(module: ModuleType, attr: str):
    has_attr = hasattr(module, attr)
    if not has_attr:
        print(f"Config file does not define '{attr}' - will be using cli arguments or default values")
    return has_attr


def _get_general_config_from_file(module, cli_config: MatchmakingConfig) -> MatchmakingConfig:
    cfg = module.GENERAL_CONFIG

    return MatchmakingConfig(
        cfg.get("CSV_DATA_DELIMITER_CHAR", cli_config.csv_cell_delimiter_char),
        cfg.get("CSV_DATA_MC_DELIMITER_CHAR", cli_config.csv_cell_mc_delimiter_char),
        cfg.get("DEFAULT_RESULT_PRECISION", cli_config.default_result_precision),
        cfg.get("DEFAULT_NUM_MAX_RESULTS_IN_GROUP", cli_config.default_num_max_results_in_group),
        cfg.get("OUTPUT_DIR", cli_config.result_output_dir),
        cfg.get("SEPARATE_RESULT_FILES_BY_GROUPS", cli_config.separate_result_files_by_groups),
        cfg.get("ON_RESULT_FILE_EXISTS_BEHAVIOUR", cli_config.on_result_file_exists_behaviour),
        cfg.get("FOOTER_CONTENT_EMAIL", cli_config.footer_content_email),
        cfg.get("FOOTER_CONTENT_PDF", cli_config.footer_content_pdf),
        cfg.get("PDF_RESULT_FILE_HEADER_DESCRIPTION", cli_config.pdf_result_file_header_description),
    )


def _get_groups_config_from_file(module, group_codes: list[str], cli_config: MatchmakingConfig) -> list[MatchGroup]:
    cfg = module.GROUPS_CONFIG
    groups_config: list[MatchGroup] = []

    for group_code in group_codes:
        if group_code in cfg:
            group_config = MatchGroup(
                group_code,
                cfg[group_code].get("TITLE", None),
                cfg[group_code].get("NUM_RESULTS_TO_SHOW", cli_config.default_num_max_results_in_group),
                cfg[group_code].get("RESULT_PRECISION", cli_config.default_result_precision),
                cfg[group_code].get("DESCRIPTION", None),
                cfg[group_code].get("RESULT_NAMES_FORMAT", None),
                cfg[group_code].get("VISIBLE_IF", None),
                cfg[group_code].get("VISIBLE_WHEN_EMPTY", False),
                cfg[group_code].get("ORDER_IN_RESULTS", -1),
            )
        else:
            print(f"Group with code {group_code} not found in GROUPS_CONFIG. Initializing with default values...")
            group_config = MatchGroup(
                group_code,
                num_results_to_show=cli_config.default_num_max_results_in_group,
                result_precision=cli_config.default_result_precision,
            )
        groups_config.append(group_config)

    return groups_config
