from utils.settings import Settings
from apps.abstract.view import AbstractView
from apps.leadLoss.dataPanel import LeadLossDataPanel
from apps.leadLoss.graphPanel import LeadLossGraphPanel

from apps.leadLoss.settingsDialogs.calculation import LeadLossCalculationSettingsDialog
from apps.leadLoss.settingsDialogs.imports import LeadLossImportSettingsDialog
from apps.type import SettingsType, TabType


class LeadLossView(AbstractView):

    def __init__(self, controller):
        super().__init__(controller)

    def createDataWidget(self):
        return LeadLossDataPanel(self.controller)

    def createGraphWidget(self):
        return LeadLossGraphPanel(self.controller)

    def getSettingsDialog(self, settingsType):
        defaultSettings = Settings.get(TabType.LEAD_LOSS, settingsType)
        if settingsType == SettingsType.IMPORT:
            return LeadLossImportSettingsDialog(defaultSettings)
        if settingsType == SettingsType.CALCULATION:
            return LeadLossCalculationSettingsDialog(defaultSettings)

        raise Exception("Unknown settingsDialogs " + str(type(settingsType)))

    ############
    ## Events ##
    ############

    def onNewlyClassifiedPoints(self, rows, concordantAges, discordantAges):
        self.graphPanel.plotDataPointsOnConcordiaAxis(rows)
        self.graphPanel.plotHistogram(concordantAges, discordantAges)

    def onNewStatistics(self, statistics):
        self.graphPanel.plotStatistics(statistics)

    def displayAgeComparison(self, rimAge, ages):
        self.graphPanel.plotAgeComparison(rimAge, ages)