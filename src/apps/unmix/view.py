from utils.settings import Settings
from apps.abstract.view import AbstractView
from apps.type import TabType, SettingsType
from apps.unmix.graphPanel import UnmixGraphPanel
from apps.unmix.dataPanel import UnmixDataPanel
from apps.unmix.settingsDialogs.calculation import UnmixCalculationSettingsDialog

from apps.unmix.settingsDialogs.imports import UnmixImportSettingsDialog


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