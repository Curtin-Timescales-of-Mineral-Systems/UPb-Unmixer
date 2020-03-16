from PyQt5.QtWidgets import *

from apps.unmix.model import Column
from apps.unmix.settings.imports import UnmixImportSettings
from apps.abstract.settingsDialogs.imports import AbstractImportSettingsDialog, ImportedValueErrorWidget, \
    GeneralSettingsWidget

from utils import stringUtils
from utils.ui.columnReferenceInput import ColumnReferenceType


class UnmixImportSettingsDialog(AbstractImportSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)

    ###############
    ## UI layout ##
    ###############

    def initCSVSettings(self):
        # Defaults
        defaults = self.defaultSettings
        columnRefs = self.defaultSettings.getDisplayColumnsAsStrings()

        self._generalSettingsWidget = GeneralSettingsWidget(self._validate, defaults)
        self._generalSettingsWidget.columnRefChanged.connect(self._onColumnRefChange)

        self._rimAgeWidget = ImportedValueErrorWidget(
            "Rim age",
            self._validate,
            defaults.columnReferenceType,
            columnRefs[Column.RIM_AGE_VALUE],
            columnRefs[Column.RIM_AGE_ERROR],
            defaults.rimAgeErrorType,
            defaults.rimAgeErrorSigmas
        )

        self._mixedUPbWidget = ImportedValueErrorWidget(
            "Mixed " + stringUtils.getUPbStr(True),
            self._validate,
            defaults.columnReferenceType,
            columnRefs[Column.MIXED_U_PB_VALUE],
            columnRefs[Column.MIXED_U_PB_ERROR],
            defaults.mixedUPbErrorType,
            defaults.mixedUPbErrorSigmas
        )

        self._mixedPbPbWidget = ImportedValueErrorWidget(
            "Mixed " + stringUtils.getPbPbStr(True),
            self._validate,
            defaults.columnReferenceType,
            columnRefs[Column.MIXED_PB_PB_VALUE],
            columnRefs[Column.MIXED_PB_PB_ERROR],
            defaults.mixedPbPbErrorType,
            defaults.mixedPbPbErrorSigmas
        )

        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)
        layout.addWidget(self._generalSettingsWidget, 0, 0)
        layout.addWidget(self._rimAgeWidget, 0, 1)
        layout.addWidget(self._mixedUPbWidget, 1, 0)
        layout.addWidget(self._mixedPbPbWidget, 1, 1)

        widget = QWidget()
        widget.setLayout(layout)
        return widget
        """
        hasHeadersLabel = self.createLabelWithHelp(
            "Has headers",
            "Does the CSV file have an initial row of column headers?"
        )
        columnDelimiterLabel = self.createLabelWithHelp(
            "Column separator",
            "Which character is used in the CSV file to separate columns?"
        )
        rimAgeLabel = self.createLabelWithHelp(
            "Rim age column",
            "Which columns are the value and error for the rim age stored in?\n" +
            "Columns may be specified either using letters (A, B, C, ...) or numbers (1, 2, 3, ...)"
        )
        uPbLabel = self.createLabelWithHelp(
            'Mixed ' + utils.U_PB_STR + ' column',
            "Which columns are the value and error for the mixed " + utils.U_PB_STR + " ratio stored in?\n" +
            "Columns may be specified either using letters (A, B, C, ...) or numbers (1, 2, 3, ...)"
        )
        pbPbLabel = self.createLabelWithHelp(
            'Mixed ' + utils.U_PB_STR + ' column',
            "Which columns are the value and error for the mixed " + utils.PB_PB_STR + " ratio stored in?\n" +
            "Columns may be specified either using letters (A, B, C, ...) or numbers (1, 2, 3, ...)"
        )
        """
        return box

    ################
    ## Validation ##
    ################

    def _onColumnRefChange(self, button):
        newRefType = ColumnReferenceType(button.option)
        self._rimAgeWidget.changeColumnReferenceType(newRefType)
        self._mixedUPbWidget.changeColumnReferenceType(newRefType)
        self._mixedPbPbWidget.changeColumnReferenceType(newRefType)

    def _createSettings(self):
        settings = UnmixImportSettings()
        settings.delimiter = self._generalSettingsWidget.getDelimiter()
        settings.hasHeaders = self._generalSettingsWidget.getHasHeaders()

        settings._columnRefs = {
            Column.RIM_AGE_VALUE: self._rimAgeWidget.getValueColumn(),
            Column.RIM_AGE_ERROR: self._rimAgeWidget.getErrorColumn(),
            Column.MIXED_U_PB_VALUE: self._mixedUPbWidget.getValueColumn(),
            Column.MIXED_U_PB_ERROR: self._mixedUPbWidget.getErrorColumn(),
            Column.MIXED_PB_PB_VALUE: self._mixedPbPbWidget.getValueColumn(),
            Column.MIXED_PB_PB_ERROR: self._mixedPbPbWidget.getErrorColumn()
        }

        settings.rimAgeErrorType = self._rimAgeWidget.getErrorType()
        settings.rimAgeErrorSigmas = self._rimAgeWidget.getErrorSigmas()
        settings.mixedUPbErrorType = self._mixedUPbWidget.getErrorType()
        settings.mixedUPbErrorSigmas = self._mixedUPbWidget.getErrorSigmas()
        settings.mixedPbPbErrorType = self._mixedPbPbWidget.getErrorType()
        settings.mixedPbPbErrorSigmas = self._mixedPbPbWidget.getErrorSigmas()

        return settings
