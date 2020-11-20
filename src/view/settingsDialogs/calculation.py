from PyQt5.QtWidgets import QFormLayout, QWidget

from model.settings.calculation import CalculationSettings
from view.settingsDialogs.abstract import AbstractSettingsDialog
from utils.ui.errorTypeInput import ErrorTypeInput


class CalculationSettingsDialog(AbstractSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)
        self.setWindowTitle("Calculation settings")

    def _init_main_settings(self):
        defaults = self.defaultSettings

        self._outputErrorSigmasRB = ErrorTypeInput(self._validate, defaults.output_error_type, defaults.output_error_sigmas)

        layout = QFormLayout()
        layout.addRow("Output error type", self._outputErrorSigmasRB)
        self._registerFormLayoutForAlignment(layout)

        box = QWidget()
        box.setLayout(layout)
        return box

    def _createSettings(self):
        settings = CalculationSettings()

        settings.output_error_type = self._outputErrorSigmasRB.getErrorType()
        settings.output_error_sigmas = self._outputErrorSigmasRB.getErrorSigmas()

        return settings
