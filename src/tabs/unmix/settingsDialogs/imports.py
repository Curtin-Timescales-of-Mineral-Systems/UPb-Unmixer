from PyQt5.QtWidgets import *

from tabs.unmix.model import Column
from tabs.unmix.settings.imports import UnmixImportSettings
from tabs.abstract.settingsDialogs.imports import AbstractImportSettingsDialog

import utils


class UnmixImportSettingsDialog(AbstractImportSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    ###############
    ## UI layout ##
    ###############

    def initErrorSettings(self):
        defaults = self.defaultSettings

        self.rimAgeSigmasRB, self.rimAgeTypeRB, rimAgeLayout = self._createErrorRow(defaults.rimAgeErrorSigmas, defaults.rimAgeErrorType)
        self.mixedPointSigmasRB, self.mixedPointTypeRB, mixedPointLayout = self._createErrorRow(defaults.mixedPointErrorSigmas, defaults.mixedPointErrorType)

        box = QGroupBox("Errors")
        layout = QFormLayout()
        layout.addRow("Rim age", rimAgeLayout)
        layout.addRow("Mixed point ratios", mixedPointLayout)
        box.setLayout(layout)
        return box

    def initCSVSettings(self):
        # Defaults
        columnRefs = self.defaultSettings.getDisplayColumnsAsStrings()
        rimAgeCol = columnRefs[Column.RIM_AGE]
        rimAgeErrorCol = columnRefs[Column.RIM_AGE_ERROR]
        uPbCol = columnRefs[Column.MIXED_U_PB]
        uPbErrorCol = columnRefs[Column.MIXED_U_PB_ERROR]
        pbPbCol = columnRefs[Column.MIXED_PB_PB]
        pbPbErrorCol = columnRefs[Column.MIXED_PB_PB_ERROR]

        self.rimAgeColumnEntry, self.rimAgeErrorColumnEntry, rimAgeColumnLayout = self._createColumnRow(rimAgeCol, rimAgeErrorCol)
        self.uPbColumnEntry, self.uPbErrorColumnEntry, uPbColumnLayout = self._createColumnRow(uPbCol, uPbErrorCol)
        self.pbPbColumnEntry, self.pbPbErrorColumnEntry, pbPbColumnLayout = self._createColumnRow(pbPbCol, pbPbErrorCol)
        
        self.delimiterEntry, self.hasHeadersCB = self._createStandardCSVFields()

        box = QGroupBox("CSV layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Has headers"), self.hasHeadersCB)
        layout.addRow(QLabel("Column delimiter"), self.delimiterEntry)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("Columns"))
        layout.addRow(QLabel('Rim age'),rimAgeColumnLayout)
        layout.addRow(QLabel(utils.U_PB_STR), uPbColumnLayout)
        layout.addRow(QLabel(utils.PB_PB_STR), pbPbColumnLayout)
        box.setLayout(layout)
        return box

    ################
    ## Validation ##
    ################

    def _createSettings(self):
        settings = UnmixImportSettings()
        settings.delimiter = self.delimiterEntry.text()
        settings.hasHeaders = self.hasHeadersCB.isChecked()

        columns = {
            Column.RIM_AGE:self.rimAgeColumnEntry.text(),
            Column.RIM_AGE_ERROR:self.rimAgeErrorColumnEntry.text(),
            Column.MIXED_U_PB:self.uPbColumnEntry.text(),
            Column.MIXED_U_PB_ERROR:self.uPbErrorColumnEntry.text(),
            Column.MIXED_PB_PB:self.pbPbColumnEntry.text(),
            Column.MIXED_PB_PB_ERROR:self.pbPbErrorColumnEntry.text()
        }
        settings._columnRefs = columns

        settings.rimAgeErrorSigmas = utils.SIGMA_OPTIONS[self.rimAgeSigmasRB.checkedId()]
        settings.rimAgeErrorType = utils.ERROR_TYPE_OPTIONS[self.rimAgeTypeRB.checkedId()]
        settings.mixedPointErrorSigmas = utils.SIGMA_OPTIONS[self.mixedPointSigmasRB.checkedId()]
        settings.mixedPointErrorType = utils.ERROR_TYPE_OPTIONS[self.mixedPointTypeRB.checkedId()]

        return settings