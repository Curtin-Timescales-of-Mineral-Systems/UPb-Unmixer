from controller.signals import Signals
from view.helpDialog import UnmixHelpDialog
from utils import csvUtils
from utils.async import AsyncTask
from utils.settings import Settings
from model.settings.type import SettingsType
from model.model import UnmixModel
from view.view import UnmixView


class UnmixTabController:

    def __init__(self):
        self.name = "Unmix rim/core"

        self.signals = Signals()
        self.signals.processingProgress.connect(self.onProcessingProgress)
        self.signals.processingCompleted.connect(self.onProcessingCompleted)
        self.signals.processingCancelled.connect(self.onProcessingCancelled)
        self.signals.processingErrored.connect(self.onProcessingErrored)

        self.view = UnmixView(self)
        self.model = UnmixModel(self.signals)

        self.worker = None

    ###########
    # Actions #
    ###########

    def importCSV(self):
        self.inputFile = self.view.getInputFile()
        if not self.inputFile:
            return

        self.view.getSettings(SettingsType.IMPORT, self._importCSVWithSettings)

    def _importCSVWithSettings(self, importSettings):
        if not importSettings:
            return
        Settings.update(importSettings)

        self._importCSV(self.inputFile, importSettings)

    def _importCSV(self, inputFile, importSettings):
        results = csvUtils.read_input(inputFile, importSettings)
        success = results is not None
        if success:
            self.model.loadRawData(importSettings, *results)
        self.view.onCSVImportFinished(success, inputFile)

    def process(self):
        self.view.getSettings(SettingsType.CALCULATION, self._processWithSettings)

    def _processWithSettings(self, processingSettings):
        if not processingSettings:
            return
        Settings.update(processingSettings)

        self.signals.processingStarted.emit()
        self.signals.taskStarted.emit("Processing data...")

        self.model.resetCalculations()
        self._process(processingSettings)

    def _process(self, calculationSettings):
        importSettings = Settings.get(SettingsType.IMPORT)
        self.worker = AsyncTask(self.signals, self.model.getProcessingFunction(), self.model.getProcessingData(),
                                importSettings, calculationSettings)
        self.worker.start()

    def cancelProcessing(self):
        if self.worker is not None:
            self.worker.halt()

    def exportCSV(self):
        outputFile = self.view.getOutputFile()
        if not outputFile:
            return

        self.signals.taskStarted.emit("Exporting CSV file")

        settings = Settings.get(SettingsType.CALCULATION)
        headers, rows = self.model.getExportData(settings)

        try:
            csvUtils.write_output(headers, rows, outputFile)
            self.signals.taskComplete.emit(True, "Successfully exported CSV file")
        except Exception as e:
            self.signals.taskComplete.emit(False, "Failed to export CSV file")
            raise e

    ##########
    # Events #
    ##########

    def onProcessingProgress(self, progressArgs):
        progress, i, row = progressArgs
        self.model.updateRow(i, row)
        self.signals.taskProgress.emit(progress)

    def onProcessingCompleted(self, output):
        self.signals.taskComplete.emit(True, "Processing complete")
        self.model.addProcessingOutput(output)

    def onProcessingCancelled(self):
        self.signals.taskComplete.emit(False, "Cancelled processing of data")

    def onProcessingErrored(self, exception):
        self.signals.taskComplete.emit(False, "Error whilst processing data")

    #################
    # Row selection #
    #################

    def selectRows(self, rowIndices):
        rows = [self.model.rows[i] for i in rowIndices]
        calculationSettings = Settings.get(SettingsType.CALCULATION)
        self.view.graphPanel.displayRows(rows, calculationSettings)

    def showHelp(self):
        dialog = UnmixHelpDialog()
        dialog.exec_()

    #########
    # Utils #
    #########

    def cheatLoad(self):
        inputFile = "/home/matthew/Code/concordia-applications/UPb-Unmixer/tests/unmixTest.csv"
        # inputFile = "C:/Users/mdagg/Documents/Programming/CurtinConcordia/tests/unmixTest.csv"
        self._importCSV(inputFile, Settings.get(SettingsType.IMPORT))
