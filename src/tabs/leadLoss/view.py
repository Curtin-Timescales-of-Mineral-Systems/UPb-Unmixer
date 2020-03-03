from model.settings import Settings
from tabs.abstract.view import AbstractView
from tabs.leadLoss.dataPanel import LeadLossDataPanel
from tabs.leadLoss.graphPanel import LeadLossGraphPanel

from tabs.leadLoss.settingsDialogs.calculation import LeadLossCalculationSettingsDialog
from tabs.leadLoss.settingsDialogs.imports import LeadLossImportSettingsDialog
from tabs.type import SettingsType, TabType


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

    def onNewConcordantPoints(self, rows, concordantAges):
        self.graphPanel.plotDataPointsOnConcordiaAxis(rows)
        self.graphPanel.plotConcordantHistogram(concordantAges)

    def onNewStatistics(self, statistics):
        self.graphPanel.plotStatistics(statistics)

    def displayAgeComparison(self, rimAge, ages):
        self.graphPanel.plotAgeComparison(rimAge, ages)