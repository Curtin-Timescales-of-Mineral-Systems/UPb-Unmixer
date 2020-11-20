from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QMessageBox, QFileDialog, QSplitter

from model.model import Model
from model.settings.type import SettingsType
from utils import config
from utils.settings import Settings
from utils.string import pluralise
from utils.ui.statusBar import StatusBarWidget
from view.dataPanel import DataPanel
from view.graphPanel import GraphPanel
from view.settingsDialogs.calculation import CalculationSettingsDialog
from view.settingsDialogs.imports import ImportSettingsDialog


class View(QDialog):
    """
    A view for the application, implemented using the PyQT framework
    """

    def __init__(self, application):
        super().__init__()

        self.setWindowTitle(config.TITLE + " (v" + config.VERSION + ")")
        self.setGeometry(10, 10, 1220, 500)
        self.setWindowFlags(self.windowFlags() & Qt.WindowMaximizeButtonHint)


        self.data_panel = DataPanel(application)
        self.graph_panel = GraphPanel()
        self.status_bar = StatusBarWidget(application.signals)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.data_panel)
        splitter.addWidget(self.graph_panel)
        splitter.setSizes([10000, 10000])
        splitter.setContentsMargins(1, 1, 1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter, 1)
        layout.addWidget(self.status_bar, 0)
        self.setLayout(layout)

        application.signals.csv_imported.connect(self.on_csv_imported)
        self.showMaximized()

    ######
    # IO #
    ######

    def get_settings(self, settingsType, callback):
        settings_popup = self.get_settings_dialog(settingsType)

        def outer_callback(result):
            if result == QDialog.Rejected:
                return None
            callback(settings_popup.settings)

        settings_popup.finished.connect(outer_callback)
        settings_popup.show()

    def get_settings_dialog(self, settingsType):
        default_settings = Settings.get(settingsType)
        if settingsType == SettingsType.IMPORT:
            return ImportSettingsDialog(default_settings)
        if settingsType == SettingsType.CALCULATION:
            return CalculationSettingsDialog(default_settings)

        raise Exception("Unknown settingsDialogs " + str(type(settingsType)))

    def get_input_file(self):
        return QFileDialog.getOpenFileName(
            caption='Open CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests',
            options=QFileDialog.DontUseNativeDialog
        )[0]

    def get_output_file(self, number_of_rejected_rows):
        message = "Is this a simple binary core-rim mixture and do your analyses cross only two age domains?"
        if number_of_rejected_rows != 0:
            message += "\n\nNote: the output contains " + pluralise("spot", number_of_rejected_rows) + " for which the " \
                       "calculated reconstructed core age has a total score of < 0.5 and therefore are deemed " \
                       "unreliable. We recommend that these ages are not used in further analysis."
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmation of assumptions")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return_value = msg.exec_()

        if return_value == QMessageBox.No:
            return

        return QFileDialog.getSaveFileName(
            caption='Save CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests',
            filter="Comma Separated Values Spreadsheet (*.csv);;",
            options=QFileDialog.DontUseNativeDialog
        )[0]

    ##########
    # Events #
    ##########

    def on_csv_imported(self, result: bool, input_file: str):
        if not result:
            self.endTask(False, "Failed to import CSV file")
            return

    def onProcessingProgress(self, progress):
        self.updateTask(progress)

    def onProcessingCompleted(self):
        self.endTask(True, "Successfully processed data")

    def onProcessingErrored(self, exception):
        self.endTask(False, "Error during processing of data")
        QMessageBox.critical(None, "Error",
                             "An error occurred during processing: \n\n" + exception.__class__.__name__ + ": " + str(
                                 exception))

    ##############
    ## Clean-up ##
    ##############

    def show_expected_error(self, error_message):
        QMessageBox.critical(None, "Error", error_message)

    def show_unexpected_error(self, error_message):
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Critical)
        popup.setText("An error occurred. Please file a bug report with the details below at "
                      "'https://github.com/Curtin-Timescales-of-Mineral-Systems/UPb-Unmixer/issues'")
        popup.setWindowTitle("Error")
        popup.setDetailedText(error_message)
        popup.setStandardButtons(QMessageBox.Ok)
        popup.exec_()