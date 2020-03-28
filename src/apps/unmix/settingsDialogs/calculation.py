from PyQt5.QtWidgets import QFormLayout, QWidget, QVBoxLayout

from utils import stringUtils
from apps.abstract.settingsDialogs.calculation import AbstractCalculationSettingsDialog
from apps.unmix.settings.calculation import UnmixCalculationSettings
from utils.ui.errorTypeInput import ErrorTypeInput
from utils.ui.radioButtonGroup import RadioButtonGroup


class UnmixCalculationSettingsDialog(AbstractCalculationSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    def initMainSettings(self):
        defaults = self.defaultSettings

        self._outputErrorSigmasRB = ErrorTypeInput(self._validate, defaults.outputErrorType, defaults.outputErrorSigmas)

        box = QWidget()
        layout = QFormLayout()
        layout.addRow("Output error type", self._outputErrorSigmasRB)
        box.setLayout(layout)
        return box

    def _createSettings(self):
        settings = UnmixCalculationSettings()

        settings.outputErrorType = self._outputErrorSigmasRB.getErrorType()
        settings.outputErrorSigmas = self._outputErrorSigmasRB.getErrorSigmas()

        return settings