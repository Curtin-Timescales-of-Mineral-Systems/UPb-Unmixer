from model.settings import Settings
from tabs.abstract.view import AbstractView
from tabs.type import TabType, SettingsType
from tabs.unmix.graphPanel import UnmixGraphPanel
from tabs.unmix.dataPanel import UnmixDataPanel
from tabs.unmix.settingsDialogs.calculation import UnmixCalculationSettingsDialog

from tabs.unmix.settingsDialogs.imports import UnmixImportSettingsDialog


class UnmixView(AbstractView):

    def __init__(self, controller):
        super().__init__(controller)

    def createDataWidget(self):
        return UnmixDataPanel(self.controller)

    def createGraphWidget(self):
        return UnmixGraphPanel(self.controller)

    def getSettingsDialog(self, settingsType):
        defaultSettings = Settings.get(TabType.UNMIX, settingsType)
        if settingsType == SettingsType.IMPORT:
            return UnmixImportSettingsDialog(defaultSettings)
        if settingsType == SettingsType.CALCULATION:
            return UnmixCalculationSettingsDialog(defaultSettings)
        #if settingsType == SettingsType.PROCESSING:
        #    return LeadLossProcessingSettingsDialog(defaultSettings)

        raise Exception("Unknown settingsDialogs " + str(type(settingsType)))