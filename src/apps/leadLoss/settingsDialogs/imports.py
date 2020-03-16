from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

from utils import stringUtils
from apps.abstract.settingsDialogs.imports import AbstractImportSettingsDialog
from apps.leadLoss.model import Column
from apps.leadLoss.settings.imports import LeadLossImportSettings


class LeadLossImportSettingsDialog(AbstractImportSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    ###############
    ## UI layout ##
    ###############

    def initErrorSettings(self):
        defaults = self.defaultSettings

        self.inputSigmasRB, self.inputTypeRB, inputLayout = self._createErrorRow(defaults.inputErrorSigmas, defaults.inputErrorType)

        box = QGroupBox("Errors")
        layout = QFormLayout()
        layout.addRow("Inputs", inputLayout)
        box.setLayout(layout)
        return box

    def initCSVSettings(self):
        columnRefs = self.defaultSettings.getDisplayColumnsAsStrings()
        uPbCol = columnRefs[Column.U_PB]
        uPbErrorCol = columnRefs[Column.U_PB_ERROR]
        pbPbCol = columnRefs[Column.PB_PB]
        pbPbErrorCol = columnRefs[Column.PB_PB_ERROR]

        self.uPbColumnEntry, self.uPbErrorColumnEntry, uPbColumnLayout = self._createColumnRow(uPbCol, uPbErrorCol)
        self.pbPbColumnEntry, self.pbPbErrorColumnEntry, pbPbColumnLayout = self._createColumnRow(pbPbCol, pbPbErrorCol)

        self.delimiterEntry, self.hasHeadersCB = self._createStandardCSVFields()

        box = QGroupBox("CSV layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Has headers"), self.hasHeadersCB)
        layout.addRow(QLabel("Column delimiter"), self.delimiterEntry)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("Columns"))
        layout.addRow(QLabel(stringUtils.U_PB_STR), uPbColumnLayout)
        layout.addRow(QLabel(stringUtils.PB_PB_STR), pbPbColumnLayout)
        box.setLayout(layout)
        return box

    ################
    ## Validation ##
    ################

    def _createSettings(self):
        settings = LeadLossImportSettings()
        settings.delimiter = self.delimiterEntry.text()
        settings.hasHeaders = self.hasHeadersCB.isChecked()
        settings.uPbColumn = self.uPbColumnEntry.text()
        settings.uPbErrorColumn = self.uPbErrorColumnEntry.text()
        settings.pbPbColumn = self.pbPbColumnEntry.text()
        settings.pbPbErrorColumn = self.pbPbErrorColumnEntry.text()
        settings.inputErrorSigmas = stringUtils.ERROR_SIGMA_OPTIONS[self.inputSigmasRB.checkedId()]
        settings.inputErrorType = stringUtils.ERROR_TYPE_OPTIONS[self.inputTypeRB.checkedId()]
        return settings