from dataclasses import dataclass
from enum import Enum


class OnResultFileExistsBehaviour(Enum):
    OVERRIDE = "override"
    SKIP = "skip"
    ASK = "ask"


@dataclass(frozen=True)
class MatchmakingConfig:
    # csv data file
    csv_cell_delimiter_char: str
    csv_cell_mc_delimiter_char: str
    # result formatting config vars
    default_result_precision: int
    default_num_max_results_in_group: int
    # output config vars
    result_output_dir: str
    separate_result_files_by_groups: bool
    on_result_file_exists_behaviour: str

    footer_content_email: str | None = None
    footer_content_pdf: str | None = None
    pdf_result_file_header_description: str | None = None

    @classmethod
    def from_argparse_args(cls, args):
        return cls(
            args.delimiter,
            args.multi_delimiter,
            args.precision,
            args.max_results_in_group,
            args.output_dir,
            args.separate_by_groups,
            args.on_file_exists,
        )
