from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QTabWidget, QWidget

from apps.unmix.helpDialog import UnmixHelpDialog
from utils import csvUtils, calculations
from utils.settings import Settings
from apps.abstract.controller import AbstractTabController
from apps.type import TabType, SettingsType
from apps.unmix.model import UnmixModel
from apps.unmix.view import UnmixView
from utils.stringUtils import U_PB_STR


class UnmixTabController(AbstractTabController):

    def __init__(self):
        super().__init__(TabType.UNMIX)

        self.name = "Unmix rim/core"
        self.view = UnmixView(self)
        self.model = UnmixModel(self.view)

        #self.cheatLoad()

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

    def showHelp(self):
        dialog = UnmixHelpDialog()
        dialog.exec_()

    ###########
    ## Utils ##
    ###########

    def cheatLoad(self):
        #inputFile = "/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests/unmixTest.csv"
        inputFile = "C:/Users/mdagg/Documents/Programming/CurtinConcordia/tests/unmixTest.csv"
        self._importCSV(inputFile, Settings.get(TabType.UNMIX, SettingsType.IMPORT))
        #self.view.getSettings(SettingsType.IMPORT, self._importCSVWithSettings)

