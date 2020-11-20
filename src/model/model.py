from typing import Tuple, List, Optional

from model.signals import Signals
from model.settings.imports import ImportSettings
from model.settings.type import SettingsType
from model.spot import Spot, SpotOutputData
from model.settings.calculation import CalculationSettings
from utils.settings import Settings


class Model:
    """
    Class that stores the application model, i.e. all the input and output data.
    """

    def __init__(self, application):
        self._application = application
        self._csv_headers: List[str] = None
        self._csv_rows: List[List[str]] = None
        self._spots = None

    def set_input_data(self,
                       import_settings: ImportSettings,
                       csv_headers: List[str],
                       csv_rows: List[List[str]]) -> None:
        self._csv_headers = csv_headers
        self._csv_rows = csv_rows
        self._spots = [Spot.parse(row, import_settings) for row in csv_rows]

        self._application.signals.headers_updated.emit()
        self._application.signals.all_rows_updated.emit()

    def get_spots(self):
        return self._spots

    def set_row_output(self, i: int, output_data: SpotOutputData) -> None:
        self._spots[i].set_output(output_data)
        self._application.signals.row_updated.emit(i)

    def clear_output_data(self) -> None:
        for row in self._spots:
            row.clear_output()

        self._application.signals.headers_updated.emit()
        self._application.signals.all_rows_updated.emit()

    def get_headers_for_display(self) -> List[str]:
        import_headers = Settings.get(SettingsType.IMPORT).get_headers_for_display()
        calculation_headers = Settings.get(SettingsType.CALCULATION).get_default_headers_for_display()
        return import_headers + calculation_headers

    def get_output_data_for_export(self, calculation_settings) -> Tuple[List[str], List[List[str]]]:
        headers = self._csv_headers + calculation_settings.get_headers_for_export()
        rows = [self._csv_rows[i] + [cell.get_export_string() for cell in self._spots[i].output_cells] for i in range(len(self._csv_rows))]
        return headers, rows

    def get_number_of_rejected_rows(self) -> int:
        return len([spot for spot in self._spots if spot.has_rejected_outputs()])
