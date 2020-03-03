import csv_mode
from model.async import AsyncTask
from model.settings import Settings
from tabs.abstract.abstractTabController import AbstractTabController
from tabs.type import TabType, SettingsType
from tabs.unmix.model import UnmixModel
from tabs.unmix.view import UnmixView

class UnmixTabController(AbstractTabController):

    def __init__(self, application):
        super().__init__(TabType.UNMIX, application)

        self.name = "Unmix"
        self.view = UnmixView(self)
        self.model = UnmixModel(self.view)

        self.cheatLoad()

    ################
    ## CSV export ##
    ################

    def exportCSV(self):
        outputFile = self.view.getOutputFile()
        if not outputFile:
            return

        self.view.startTask("Exporting CSV file")

        settings = Settings.get(TabType.UNMIX, SettingsType.CALCULATION)
        headers, rows = self.model.getExportData(settings)

        try:
            csv_mode.write_output(headers, rows, outputFile)
            self.view.endTask(True, "Successfully exported CSV file")
        except Exception as e:
            self.view.endTask(False, "Failed to export CSV file")

    ################
    ## Processing ##
    ################


    """
    def startProcessing(self):
        if not self.haltEvent.is_set():
            self.processButton.setText(self.processButton.originalText)
            self.haltEvent.set()
            return

        self.view.startTask("Processing CSV file...", len(self.rows), self._progressSignal)
        self.runAsyncTask(self._process, self._endProcessing, self.processButton, "Cancel processing")
        self._progressSignal.connect(self._onRowProcessed)

    def _endProcessing(self, complete, result):
        self._progressSignal.disconnect(self._onRowProcessed)

        if not complete:
            self.view.endTask(False, "Cancelled processing of data")
            return

        self.view.endTask(True, "Successfully processed data")

    def onProcessingCompleted(self):
        print("Processing complete")
    """

    def onProcessingProgress(self, progressArgs):
        progress, i, row = progressArgs
        self.model.updateRow(i, row)
        self.view.onProcessingProgress(progress, i, row)

    ###################
    ## Row selection ##
    ###################

    def selectRows(self, rowIndices):
        rows = [self.model.rows[i] for i in rowIndices]
        calculationSettings = Settings.get(self.tabType, SettingsType.CALCULATION)
        self.view.graphPanel.displayRows(rows, calculationSettings)

    ###########
    ## Utils ##
    ###########

    def cheatLoad(self):
        inputFile = "/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests/unmixTest.csv"
        self._importCSV(inputFile, Settings.get(TabType.UNMIX, SettingsType.IMPORT))
