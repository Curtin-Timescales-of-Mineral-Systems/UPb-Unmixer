from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from model.column import Column
from model.settings.columnIndex import ColumnReferenceType
from model.settings.imports import ImportSettings
from view.settingsDialogs.abstract import AbstractSettingsDialog

from utils import string
from utils.ui import uiUtils
from utils.ui.columnReferenceInput import ColumnReferenceInput
from utils.ui.columnReferenceTypeInput import ColumnReferenceTypeInput
from utils.ui.errorTypeInput import ErrorTypeInput


class ImportSettingsDialog(AbstractSettingsDialog):

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)
        self.setWindowTitle("CSV import settings")

    ###############
    ## UI layout ##
    ###############

    def _init_main_settings(self):
        # Defaults
        defaults = self.defaultSettings
        column_refs = self.defaultSettings.get_input_columns_by_indices()

        self._generalSettingsWidget = GeneralSettingsWidget(self._validate, defaults)
        self._generalSettingsWidget.columnRefChanged.connect(self._onColumnRefChange)

        self._rimAgeWidget = ImportedValueErrorWidget(
            "Rim age",
            self._validate,
            defaults.column_reference_type,
            column_refs[Column.RIM_AGE_VALUE],
            column_refs[Column.RIM_AGE_ERROR],
            defaults.rim_age_error_type,
            defaults.rim_age_error_sigmas
        )

        self._mixedUPbWidget = ImportedValueErrorWidget(
            "Mixed " + string.getUPbStr(True),
            self._validate,
            defaults.column_reference_type,
            column_refs[Column.MIXED_U_PB_VALUE],
            column_refs[Column.MIXED_U_PB_ERROR],
            defaults.mixed_uPb_error_type,
            defaults.mixed_uPb_error_sigmas
        )

        self._mixedPbPbWidget = ImportedValueErrorWidget(
            "Mixed " + string.getPbPbStr(True),
            self._validate,
            defaults.column_reference_type,
            column_refs[Column.MIXED_PB_PB_VALUE],
            column_refs[Column.MIXED_PB_PB_ERROR],
            defaults.mixed_pbPb_error_type,
            defaults.mixed_pbPb_error_sigmas
        )

        self._uThConcentrationWidget = UThConcentrationWidget(
            self._validate,
            defaults.column_reference_type,
            column_refs[Column.U_CONCENTRATION],
            column_refs[Column.TH_CONCENTRATION]
        )

        self._updateColumnRefs(defaults.column_reference_type)

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
        new_ref_type = ColumnReferenceType(button.option)
        self._updateColumnRefs(new_ref_type)
        self._validate()

    def _updateColumnRefs(self, newRefType):
        self._rimAgeWidget.changeColumnReferenceType(newRefType)
        self._mixedUPbWidget.changeColumnReferenceType(newRefType)
        self._mixedPbPbWidget.changeColumnReferenceType(newRefType)

    def _createSettings(self):
        settings = ImportSettings()
        settings.csv_delimiter = self._generalSettingsWidget.getDelimiter()
        settings.csv_has_headers = self._generalSettingsWidget.getHasHeaders()
        settings.column_reference_type = self._generalSettingsWidget.getColumnReferenceType()

        settings._column_references = {
            Column.RIM_AGE_VALUE: self._rimAgeWidget.getValueColumn(),
            Column.RIM_AGE_ERROR: self._rimAgeWidget.getErrorColumn(),
            Column.MIXED_U_PB_VALUE: self._mixedUPbWidget.getValueColumn(),
            Column.MIXED_U_PB_ERROR: self._mixedUPbWidget.getErrorColumn(),
            Column.MIXED_PB_PB_VALUE: self._mixedPbPbWidget.getValueColumn(),
            Column.MIXED_PB_PB_ERROR: self._mixedPbPbWidget.getErrorColumn(),
            Column.U_CONCENTRATION: self._uThConcentrationWidget.getUColumn(),
            Column.TH_CONCENTRATION: self._uThConcentrationWidget.getThColumn(),
        }

        settings.rim_age_error_type = self._rimAgeWidget.getErrorType()
        settings.rim_age_error_sigmas = self._rimAgeWidget.getErrorSigmas()
        settings.mixed_uPb_error_type = self._mixedUPbWidget.getErrorType()
        settings.mixed_uPb_error_sigmas = self._mixedUPbWidget.getErrorSigmas()
        settings.mixed_pbPb_error_type = self._mixedPbPbWidget.getErrorType()
        settings.mixed_pbPb_error_sigmas = self._mixedPbPbWidget.getErrorSigmas()

        return settings


class GeneralSettingsWidget(QGroupBox):

    def __init__(self, validation, defaultSettings):
        super().__init__("General settings")

        self._delimiterEntry = QLineEdit(defaultSettings.csv_delimiter)
        self._delimiterEntry.textChanged.connect(validation)
        self._delimiterEntry.setFixedWidth(30)
        self._delimiterEntry.setAlignment(Qt.AlignCenter)

        self._hasHeadersCB = QCheckBox()
        self._hasHeadersCB.setChecked(defaultSettings.csv_has_headers)
        self._hasHeadersCB.stateChanged.connect(validation)

        self._columnRefType = ColumnReferenceTypeInput(validation, defaultSettings.column_reference_type)
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


class ImportedValueErrorWidget(QGroupBox):
    """
    A widget for importing an (value, error) pair
    """
    width = 30

    def __init__(self,
                 title,
                 validation,
                 defaultReferenceType,
                 defaultValueColumn,
                 defaultErrorColumn,
                 defaultErrorType, defaultErrorSigmas):
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

    def getValueColumn(self) -> int:
        return self._valueColumn.get_column_index()

    def getErrorColumn(self) -> int:
        return self._errorColumn.get_column_index()

    def getErrorType(self):
        return self._errorType.getErrorType()

    def getErrorSigmas(self):
        return self._errorType.getErrorSigmas()

    def changeColumnReferenceType(self, newReferenceType):
        self._valueColumn.set_column_reference_type(newReferenceType)
        self._errorColumn.set_column_reference_type(newReferenceType)


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
        return self._uColumn.get_column_index()

    def getThColumn(self):
        return self._thColumn.get_column_index()

    def changeColumnReferenceType(self, newReferenceType):
        self._uColumn.set_column_reference_type(newReferenceType)
        self._thColumn.set_column_reference_type(newReferenceType)
