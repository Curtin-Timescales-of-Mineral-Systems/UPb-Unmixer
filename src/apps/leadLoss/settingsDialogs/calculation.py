from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit

from utils import stringUtils
from apps.abstract.settingsDialogs.calculation import AbstractCalculationSettingsDialog
from apps.leadLoss.settings.calculation import LeadLossCalculationSettings
from apps.type import TabType, SettingsType


class LeadLossCalculationSettingsDialog(AbstractCalculationSettingsDialog):

    KEY = (TabType.LEAD_LOSS, SettingsType.CALCULATION)

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.initDiscordanceSettings())
        self.layout.addWidget(self.initButtons())
        self.setLayout(self.layout)

    def initDiscordanceSettings(self):
        box = QGroupBox("Discordance")

        self.discordanceTypeRB, discordanceTypeRBLayout = self._createRadioButtons(stringUtils.DISCORDANCE_OPTIONS, "Percentages")
        self.discordancePercentageCutoffLE = QLineEdit("10.0")

        self.discordancePercentageCutoffLE.textChanged.connect(self._validate)

        layout = QFormLayout()
        layout.addRow(QLabel("Use:"), discordanceTypeRBLayout)
        layout.addRow("Percentage cutoff:", self.discordancePercentageCutoffLE)
        box.setLayout(layout)
        return box

    #####################
    ## Create settings ##
    #####################

    def _createSettings(self):
        settings = LeadLossCalculationSettings()

        settings.discordanceType = stringUtils.DISCORDANCE_OPTIONS[self.discordanceTypeRB.checkedId()]
        if settings.discordanceType == "Percentages":
            settings.discordancePercentageCutoff = float(self.discordancePercentageCutoffLE.text())/100

        return settings