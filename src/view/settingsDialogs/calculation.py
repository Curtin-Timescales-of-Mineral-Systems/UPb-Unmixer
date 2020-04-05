from PyQt5.QtWidgets import QFormLayout, QWidget

from model.settings.calculation import UnmixCalculationSettings
from view.settingsDialogs.abstract import AbstractSettingsDialog
from utils.ui.errorTypeInput import ErrorTypeInput


class UnmixCalculationSettingsDialog(AbstractSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)
        self.setWindowTitle("Calculation settings")

    def initMainSettings(self):
        defaults = self.defaultSettings

        self._outputErrorSigmasRB = ErrorTypeInput(self._validate, defaults.outputErrorType, defaults.outputErrorSigmas)

        layout = QFormLayout()
        layout.addRow("Output error type", self._outputErrorSigmasRB)
        self._registerFormLayoutForAlignment(layout)

        box = QWidget()
        box.setLayout(layout)
        return box

    def _createSettings(self):
        settings = UnmixCalculationSettings()

        settings.outputErrorType = self._outputErrorSigmasRB.getErrorType()
        settings.outputErrorSigmas = self._outputErrorSigmasRB.getErrorSigmas()

        return settings
