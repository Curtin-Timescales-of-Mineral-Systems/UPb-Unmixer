from utils import csvUtils
from utils.settings import Settings
from apps.abstract.controller import AbstractTabController
from apps.type import TabType, SettingsType
from apps.unmix.model import UnmixModel
from apps.unmix.view import UnmixView


class UnmixTabController(AbstractTabController):

    def __init__(self):
        super().__init__(TabType.UNMIX)

        self.name = "Unmix rim/core"
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
            csvUtils.write_output(headers, rows, outputFile)
            self.view.endTask(True, "Successfully exported CSV file")
        except Exception as e:
            self.view.endTask(False, "Failed to export CSV file")
            raise e

    ################
    ## Processing ##
    ################

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
        # self._importCSV(inputFile, Settings.get(TabType.UNMIX, SettingsType.IMPORT))
        self.view.getSettings(SettingsType.IMPORT, self._importCSVWithSettings)
