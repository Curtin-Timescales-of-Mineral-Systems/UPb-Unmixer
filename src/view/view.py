from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSplitter, QVBoxLayout, QDialog, QMessageBox, QWidget

from utils.settings import Settings
from model.settings.type import SettingsType
from utils.stringUtils import pluralise
from view.graphPanel import UnmixGraphPanel
from view.dataPanel import UnmixDataPanel
from view.settingsDialogs.calculation import UnmixCalculationSettingsDialog

from view.settingsDialogs.imports import UnmixImportSettingsDialog
from utils.ui.statusBar import StatusBarWidget


class UnmixView(QWidget):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.initUI()

        self.controller.signals.csvImported.connect(self.onCSVImportFinished)

    def initUI(self):
        self.graphPanel = self.createGraphWidget()
        self.dataPanel = self.createDataWidget()
        self.statusBar = StatusBarWidget(self.controller.signals)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.dataPanel)
        splitter.addWidget(self.graphPanel)
        splitter.setSizes([10000, 10000])
        splitter.setContentsMargins(1, 1, 1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter, 1)
        layout.addWidget(self.statusBar, 0)
        self.setLayout(layout)

    ########
    ## IO ##
    ########

    def createDataWidget(self):
        return UnmixDataPanel(self.controller)

    def createGraphWidget(self):
        return UnmixGraphPanel(self.controller)

    def getSettingsDialog(self, settingsType):
        defaultSettings = Settings.get(settingsType)
        if settingsType == SettingsType.IMPORT:
            return UnmixImportSettingsDialog(defaultSettings)
        if settingsType == SettingsType.CALCULATION:
            return UnmixCalculationSettingsDialog(defaultSettings)

        raise Exception("Unknown settingsDialogs " + str(type(settingsType)))

    def getInputFile(self):
        return QFileDialog.getOpenFileName(
            caption='Open CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests'
        )[0]

    def getOutputFile(self, numberOfRejectedRows):
        message = "Is this a simple binary core-rim mixture and do your analyses cross only two age domains?"
        if numberOfRejectedRows != 0:
            message +=  "\n\nNote: the output contains " + pluralise("spot", numberOfRejectedRows) + " for which the " \
                        "calculated reconstructed core age has a total score of < 0.5 and therefore are deemed " \
                        "unreliable. We recommend that these ages are not used in further analysis."
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmation of assumptions")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()

        if retval == QMessageBox.No:
            return

        return QFileDialog.getSaveFileName(
            caption='Save CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests',
            filter="Comma Separated Values Spreadsheet (*.csv);;"
        )[0]

    def getSettings(self, settingsType, callback):
        settingsPopup = self.getSettingsDialog(settingsType)

        def outerCallback(result):
            if result == QDialog.Rejected:
                return None
            callback(settingsPopup.settings)

        settingsPopup.finished.connect(outerCallback)
        settingsPopup.show()

    ############
    ## Events ##
    ############

    def onCSVImportFinished(self, result, inputFile):
        if not result:
            self.endTask(False, "Failed to import CSV file")
            return

        self.dataPanel.afterSuccessfulCSVImport(inputFile)

    def onProcessingProgress(self, progress, *args):
        self.updateTask(progress)

    def onProcessingCompleted(self):
        self.endTask(True, "Successfully processed data")

    def onProcessingCancelled(self):
        pass

    def onProcessingErrored(self, exception):
        self.endTask(False, "Error during processing of data")
        QMessageBox.critical(None, "Error",
                             "An error occurred during processing: \n\n" + exception.__class__.__name__ + ": " + str(
                                 exception))

    ##############
    ## Clean-up ##
    ##############

    def closeEvent(self, event):
        self.haltEvent.set()
