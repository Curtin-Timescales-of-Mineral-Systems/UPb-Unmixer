from PyQt5.QtWidgets import QFormLayout, QWidget, QVBoxLayout

from utils import stringUtils
from apps.abstract.settingsDialogs.calculation import AbstractCalculationSettingsDialog
from apps.unmix.settings.calculation import UnmixCalculationSettings


class UnmixCalculationSettingsDialog(AbstractCalculationSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.initErrorSettings())
        self.layout.addWidget(self.initButtons())
        self.setLayout(self.layout)

    def initErrorSettings(self):
        defaults = self.defaultSettings
        self.outputSigmasRB, self.outputTypeRB, outputLayout = self._createErrorRow(defaults.outputErrorSigmas, defaults.outputErrorType)

        box = QWidget()
        layout = QFormLayout()
        layout.addRow("Output", outputLayout)
        box.setLayout(layout)
        return box

    def _createSettings(self):
        settings = UnmixCalculationSettings()

        settings.outputErrorSigmas = stringUtils.SIGMA_OPTIONS[self.outputSigmasRB.checkedId()]
        settings.outputErrorType = stringUtils.ERROR_TYPE_OPTIONS[self.outputTypeRB.checkedId()]

        return settings