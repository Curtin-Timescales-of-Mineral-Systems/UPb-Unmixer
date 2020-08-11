from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from model.column import Column
from model.settings.imports import UnmixImportSettings
from view.settingsDialogs.abstract import AbstractSettingsDialog

from utils import stringUtils
from utils.csvUtils import ColumnReferenceType
from utils.ui import uiUtils
from utils.ui.columnReferenceInput import ColumnReferenceInput
from utils.ui.columnReferenceTypeInput import ColumnReferenceTypeInput
from utils.ui.errorTypeInput import ErrorTypeInput


class UnmixImportSettingsDialog(AbstractSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)
        self.setWindowTitle("CSV import settings")

    ###############
    ## UI layout ##
    ###############

    def initMainSettings(self):
        # Defaults
        defaults = self.defaultSettings
        columnRefs = self.defaultSettings.getDisplayColumnsByRefs()

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

        self._uThConcentrationWidget = UThConcentrationWidget(
            self._validate,
            defaults.columnReferenceType,
            columnRefs[Column.U_CONCENTRATION],
            columnRefs[Column.TH_CONCENTRATION]
        )

        self._updateColumnRefs(defaults.columnReferenceType)

        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)
        layout.addWidget(self._generalSettingsWidget, 0, 0)
        layout.addWidget(self._rimAgeWidget, 0, 1)
        layout.addWidget(self._mixedUPbWidget, 1, 0)
        layout.addWidget(self._mixedPbPbWidget, 1, 1)
        layout.addWidget(self._uThConcentrationWidget, 2, 0)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    ################
    ## Validation ##
    ################

    def _onColumnRefChange(self, button):
        newRefType = ColumnReferenceType(button.option)
        self._updateColumnRefs(newRefType)
        self._validate()

    def _updateColumnRefs(self, newRefType):
        self._rimAgeWidget.changeColumnReferenceType(newRefType)
        self._mixedUPbWidget.changeColumnReferenceType(newRefType)
        self._mixedPbPbWidget.changeColumnReferenceType(newRefType)

    def _createSettings(self):
        settings = UnmixImportSettings()
        settings.delimiter = self._generalSettingsWidget.getDelimiter()
        settings.hasHeaders = self._generalSettingsWidget.getHasHeaders()
        settings.columnReferenceType = self._generalSettingsWidget.getColumnReferenceType()

        settings._columnRefs = {
            Column.RIM_AGE_VALUE: self._rimAgeWidget.getValueColumn(),
            Column.RIM_AGE_ERROR: self._rimAgeWidget.getErrorColumn(),
            Column.MIXED_U_PB_VALUE: self._mixedUPbWidget.getValueColumn(),
            Column.MIXED_U_PB_ERROR: self._mixedUPbWidget.getErrorColumn(),
            Column.MIXED_PB_PB_VALUE: self._mixedPbPbWidget.getValueColumn(),
            Column.MIXED_PB_PB_ERROR: self._mixedPbPbWidget.getErrorColumn(),
            Column.U_CONCENTRATION: self._uThConcentrationWidget.getUColumn(),
            Column.TH_CONCENTRATION: self._uThConcentrationWidget.getThColumn(),
        }

        settings.rimAgeErrorType = self._rimAgeWidget.getErrorType()
        settings.rimAgeErrorSigmas = self._rimAgeWidget.getErrorSigmas()
        settings.mixedUPbErrorType = self._mixedUPbWidget.getErrorType()
        settings.mixedUPbErrorSigmas = self._mixedUPbWidget.getErrorSigmas()
        settings.mixedPbPbErrorType = self._mixedPbPbWidget.getErrorType()
        settings.mixedPbPbErrorSigmas = self._mixedPbPbWidget.getErrorSigmas()

        return settings




class GeneralSettingsWidget(QGroupBox):

    def __init__(self, validation, defaultSettings):
        super().__init__("General settings")

        self._delimiterEntry = QLineEdit(defaultSettings.delimiter)
        self._delimiterEntry.textChanged.connect(validation)
        self._delimiterEntry.setFixedWidth(30)
        self._delimiterEntry.setAlignment(Qt.AlignCenter)

        self._hasHeadersCB = QCheckBox()
        self._hasHeadersCB.setChecked(defaultSettings.hasHeaders)
        self._hasHeadersCB.stateChanged.connect(validation)

        self._columnRefType = ColumnReferenceTypeInput(validation, defaultSettings.columnReferenceType)
        self.columnRefChanged = self._columnRefType.group.buttonReleased

        layout = QFormLayout()
        layout.setHorizontalSpacing(uiUtils.FORM_HORIZONTAL_SPACING)
        layout.addRow("File headers", self._hasHeadersCB)
        layout.addRow("Column separator", self._delimiterEntry)
        layout.addRow("Refer to columns by", self._columnRefType)
        self.setLayout(layout)

    def getHasHeaders(self):
        return self._hasHeadersCB.isChecked()

    def getDelimiter(self):
        return self._delimiterEntry.text()

    def getColumnReferenceType(self):
        return self._columnRefType.selection()

# A widget for importing an (value, error) pair

class ImportedValueErrorWidget(QGroupBox):
    width = 30

    def __init__(self, title, validation, defaultReferenceType, defaultValueColumn, defaultErrorColumn, defaultErrorType, defaultErrorSigmas):
        super().__init__(title)

        self._valueColumn = ColumnReferenceInput(validation, defaultReferenceType, defaultValueColumn)
        self._errorColumn = ColumnReferenceInput(validation, defaultReferenceType, defaultErrorColumn)
        self._errorType = ErrorTypeInput(validation, defaultErrorType, defaultErrorSigmas)

        layout = QFormLayout()
        layout.setHorizontalSpacing(uiUtils.FORM_HORIZONTAL_SPACING)
        layout.addRow("Value column", self._valueColumn)
        layout.addRow("Error column", self._errorColumn)
        layout.addRow("Error type", self._errorType)
        self.setLayout(layout)

    def getValueColumn(self):
        return self._valueColumn.text()

    def getErrorColumn(self):
        return self._errorColumn.text()

    def getErrorType(self):
        return self._errorType.getErrorType()

    def getErrorSigmas(self):
        return self._errorType.getErrorSigmas()

    def changeColumnReferenceType(self, newReferenceType):
        self._valueColumn.changeColumnReferenceType(newReferenceType)
        self._errorColumn.changeColumnReferenceType(newReferenceType)

class UThConcentrationWidget(QGroupBox):

    def __init__(self, validation, defaultColumnReferenceType, uConcentrationDefaultValue, thConcentrationDefaultValue):
        super().__init__("U and Th concentrations")

        self._uColumn = ColumnReferenceInput(validation, defaultColumnReferenceType, uConcentrationDefaultValue)
        self._thColumn = ColumnReferenceInput(validation, defaultColumnReferenceType, thConcentrationDefaultValue)

        layout = QFormLayout()
        layout.setHorizontalSpacing(uiUtils.FORM_HORIZONTAL_SPACING)
        layout.addRow("U concentration (ppm) column", self._uColumn)
        layout.addRow("Th concentration (ppm) column", self._thColumn)
        self.setLayout(layout)

    def getUColumn(self):
        return self._uColumn.text()

    def getThColumn(self):
        return self._thColumn.text()

    def changeColumnReferenceType(self, newReferenceType):
        self._uColumn.changeColumnReferenceType(newReferenceType)
        self._thColumn.changeColumnReferenceType(newReferenceType)