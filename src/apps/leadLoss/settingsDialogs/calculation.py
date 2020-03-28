from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QWidget

from utils import stringUtils
from apps.abstract.settingsDialogs.calculation import AbstractCalculationSettingsDialog
from apps.leadLoss.settings.calculation import LeadLossCalculationSettings
from apps.type import TabType, SettingsType
from utils.ui.ageInput import AgeInput
from utils.ui.radioButtonGroup import RadioButtonGroup, IntRadioButtonGroup


class LeadLossCalculationSettingsDialog(AbstractCalculationSettingsDialog):

    KEY = (TabType.LEAD_LOSS, SettingsType.CALCULATION)

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

        self._onDiscordanceTypeChanged()

    def initMainSettings(self):
        layout = QVBoxLayout()
        layout.addWidget(self._initDiscordanceSettings())
        layout.addWidget(self._initSamplingSettings())
        layout.addWidget(self._initDistributionComparisonSettings())

        widget = QWidget()
        widget.setLayout(layout)
        return widget


    def _initDiscordanceSettings(self):
        defaults = self.defaultSettings

        self.discordanceTypeRB = RadioButtonGroup(stringUtils.DISCORDANCE_OPTIONS, self._validate, defaults.discordanceType)
        self.discordanceTypeRB.group.buttonClicked.connect(self._onDiscordanceTypeChanged)

        self.discordancePercentageCutoffLE = QLineEdit(str(defaults.discordancePercentageCutoff))
        self.discordancePercentageCutoffLE.textChanged.connect(self._validate)
        self.discordancePercentageCutoffLabel = QLabel("Percentage cutoff")

        self.discordanceEllipseSigmasRB = IntRadioButtonGroup(stringUtils.ERROR_SIGMA_OPTIONS, self._validate, defaults.discordanceEllipseSigmas)
        self.discordanceEllipseSigmasLabel = QLabel("Ellipse sigmas")

        self.discordanceLayout = QFormLayout()
        self.discordanceLayout.addRow("Classify using", self.discordanceTypeRB)
        self.discordanceLayout.addRow(self.discordancePercentageCutoffLabel, self.discordancePercentageCutoffLE)
        self.discordanceLayout.addRow(self.discordanceEllipseSigmasLabel, self.discordanceEllipseSigmasRB)
        self.discordanceLayout.setHorizontalSpacing(20)

        box = QGroupBox("Discordance")
        box.setLayout(self.discordanceLayout)
        return box

    def _initSamplingSettings(self):
        defaults = self.defaultSettings

        self.minimumRimAgeInput = AgeInput(self._validate, defaults.minimumRimAge)
        self.maximumRimAgeInput = AgeInput(self._validate, defaults.maximumRimAge)
        self.samplingResolutionInput = AgeInput(self._validate, defaults.minimumRimAge)

        layout = QFormLayout()
        layout.addRow("Minimum rim age", self.minimumRimAgeInput)
        layout.addRow("Maximum rim age", self.maximumRimAgeInput)
        layout.addRow("Sampling resolution", self.samplingResolutionInput)

        box = QGroupBox("Rim age sampling")
        box.setLayout(layout)
        return box

    def _initDistributionComparisonSettings(self):
        defaults = self.defaultSettings

        layout = QFormLayout()

        box = QGroupBox("Distribution comparison")
        box.setLayout(layout)
        return box

    ############
    ## Events ##
    ############

    def _onDiscordanceTypeChanged(self):
        type = self.discordanceTypeRB.getSelection()
        percentages = type == "Percentages"
        self.discordancePercentageCutoffLabel.setVisible(percentages)
        self.discordancePercentageCutoffLE.setVisible(percentages)
        self.discordanceEllipseSigmasLabel.setVisible(not percentages)
        self.discordanceEllipseSigmasRB.setVisible(not percentages)

    #####################
    ## Create settings ##
    #####################

    def _createSettings(self):
        settings = LeadLossCalculationSettings()

        settings.discordanceType = self.discordanceTypeRB.getSelection()
        if settings.discordanceType == "Percentages":
            settings.discordancePercentageCutoff = float(self.discordancePercentageCutoffLE.text())/100
        else:
            settings.discordanceEllipseSigmas = self.discordanceEllipseSigmasRB.getSelection()

        settings.minimumRimAge = self.minimumRimAgeInput.getAge()
        settings.maximumRimAge = self.maximumRimAgeInput.getAge()
        settings.samplingResolution = self.samplingResolutionInput.getAge()
        return settings