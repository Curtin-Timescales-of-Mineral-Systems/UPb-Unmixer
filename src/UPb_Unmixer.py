import multiprocessing
import sys
import traceback
from typing import List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyleFactory

from model.model import Model
from model.spot import Spot
from model.settings.calculation import CalculationSettings
from model.settings.imports import ImportSettings
from model.settings.type import SettingsType
from model.signals import Signals
from processing import process_spots
from utils import csvUtils
from utils.asynchronous import AsyncTask
from utils.exception import ExpectedException
from utils.settings import Settings
from view.helpDialog import HelpDialog
from view.view import View


class Application:

    def __init__(self):
        # Necessary for building executable with Pyinstaller correctly on Windows
        # (see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing)
        multiprocessing.freeze_support()

        # Reroute exceptions to display a message box to the user
        sys.excepthook = self.exception_hook

        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon("../resources/icon.ico"))

        self.signals: Signals = Signals()
        self.signals.processing_progress.connect(self.onProcessingProgress)
        self.signals.processing_completed.connect(self.onProcessingCompleted)
        self.signals.processing_cancelled.connect(self.onProcessingCancelled)
        self.signals.processing_errored.connect(self.onProcessingErrored)

        self.worker: AsyncTask = None
        self.model: Model = Model(self)
        self.view: View = View(self)

        sys.exit(app.exec_())

    #############
    # Importing #
    #############

    def import_csv(self) -> None:
        input_file = self.view.get_input_file()
        if not input_file:
            return

        Settings.set_current_file(input_file)

        def callback(settings: ImportSettings):
            if not settings:
                return
            Settings.update(settings)
            self._import_csv(input_file, settings)

        self.view.get_settings(SettingsType.IMPORT, callback)

    def _import_csv(self, input_file: str, settings: ImportSettings) -> None:
        results = csvUtils.read_input(input_file, settings)
        success = results is not None
        if success:
            self.model.set_input_data(settings, *results)
            self.signals.task_complete.emit(True, "Successfully imported CSV file")
        self.signals.csv_imported.emit(success, input_file)

    ##############
    # Processing #
    ##############

    def process(self) -> None:
        def callback(settings: CalculationSettings):
            if not settings:
                return
            Settings.update(settings)

            self.signals.processing_started.emit()
            self.signals.task_started.emit("Processing data...")

            self.model.clear_output_data()
            self._process(settings)

        self.view.get_settings(SettingsType.CALCULATION, callback)

    def _process(self, settings: CalculationSettings) -> None:
        self.worker = AsyncTask(self.signals, process_spots, self.model._spots, settings)
        self.worker.start()

    def cancelProcessing(self) -> None:
        if self.worker is not None:
            self.worker.halt()

    #############
    # Exporting #
    #############

    def exportCSV(self) -> None:
        number_of_rejected_rows = self.model.get_number_of_rejected_rows()
        output_file = self.view.get_output_file(number_of_rejected_rows)
        if not output_file:
            return

        self.signals.task_started.emit("Exporting CSV file")

        settings = Settings.get(SettingsType.CALCULATION)
        headers, rows = self.model.get_output_data_for_export(settings)

        try:
            csvUtils.write_output(headers, rows, output_file)
            self.signals.task_complete.emit(True, "Successfully exported CSV file")
        except Exception as e:
            self.signals.task_complete.emit(False, "Failed to export CSV file")
            raise e

    def show_help(self) -> None:
        dialog = HelpDialog()
        dialog.exec_()

    ##########
    # Events #
    ##########

    def onProcessingProgress(self, progressArgs) -> None:
        progress, i, output_data = progressArgs
        self.model.set_row_output(i, output_data)
        self.signals.task_progress.emit(progress)

    def onProcessingCompleted(self) -> None:
        self.signals.task_complete.emit(True, "Processing complete")

    def onProcessingCancelled(self) -> None:
        self.signals.task_complete.emit(False, "Cancelled processing of data")

    def onProcessingErrored(self, exception: Exception) -> None:
        self.signals.task_complete.emit(False, "Error whilst processing data")
        raise Exception(exception)

    #################
    # Row selection #
    #################

    def selectRows(self, rowIndices) -> None:
        rows = [self.model._spots[i] for i in rowIndices]
        calculation_settings = Settings.get(SettingsType.CALCULATION)
        self.view.graph_panel.displayRows(rows, calculation_settings)

    #########
    # Utils #
    #########

    def exception_hook(self, exception_type, value, tb) -> None:
        """
        Method to hook into Python's exception handling mechanism to display any errors that occur in the UI
        as well as in the console.
        """
        if isinstance(value, ExpectedException):
            self.view.show_expected_error(str(value))
            return

        sys.__excepthook__(exception_type, value, tb)
        error = str(value) + "\n" + "".join(traceback.format_tb(tb))
        self.view.show_unexpected_error(error)

    def cheat_load(self) -> None:
        """
        Method for automatically loading a CSV during development. Call in the constructor of this class
        """
        input_file = "/home/matthew/Code/concordia-applications/UPb-Unmixer/tests/unmixTest.csv"
        Settings.set_current_file(input_file)
        # input_file = "C:/Users/mdagg/Documents/Programming/CurtinConcordia/tests/unmixTest.csv"
        self._import_csv(input_file, Settings.get(SettingsType.IMPORT))


if __name__ == '__main__':
    app = Application()
