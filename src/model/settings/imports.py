from typing import Dict, List

from model.column import Column
from model.settings.columnIndex import ColumnReferenceType, ColumnIndex
from utils import string, csvUtils

from model.settings.type import SettingsType


class ImportSettings:
    """
    User settings for importing data from a CSV file into the application.
    """
    KEY = SettingsType.IMPORT

    def __init__(self):
        self.csv_delimiter: str = ","
        self.csv_has_headers: bool = True

        self.column_reference_type: ColumnReferenceType = ColumnReferenceType.LETTERS
        self._column_references: dict[Column, int] = {col: i for i, col in enumerate(Column)}

        self.rim_age_error_type: str = "Absolute"
        self.rim_age_error_sigmas: int = 2

        self.mixed_uPb_error_type: str = "Absolute"
        self.mixed_uPb_error_sigmas: int = 2

        self.mixed_pbPb_error_type: str = "Absolute"
        self.mixed_pbPb_error_sigmas: int = 2

    def get_largest_column_asked_for(self) -> int:
        return max(self._column_references.values())

    def get_input_columns_by_indices(self) -> Dict[Column, int]:
        return self._column_references

    def get_headers_for_display(self) -> List[str]:
        return [
            "Rim age (Ma)",
            "±" + string.get_error_str(self.rim_age_error_sigmas, self.rim_age_error_type),
            "Mixed " + string.U_PB_STR,
            "±" + string.get_error_str(self.mixed_uPb_error_sigmas, self.mixed_uPb_error_type),
            "Mixed " + string.PB_PB_STR,
            "±" + string.get_error_str(self.mixed_pbPb_error_sigmas, self.mixed_pbPb_error_type),
            "U ppm",
            "Th ppm"
        ]

    def validate(self) -> str:
        if not all([v is not None for v in self._column_references.values()]):
            return "Must enter a value for each column"

        display_columns = self._column_references.values()
        if len(set(display_columns)) != len(display_columns):
            return "Columns should not contain duplicates"

        return None

    def upgrade_to_version_1p1(self) -> None:
        self._column_references[Column.U_CONCENTRATION] = 6
        self._column_references[Column.TH_CONCENTRATION] = 7
