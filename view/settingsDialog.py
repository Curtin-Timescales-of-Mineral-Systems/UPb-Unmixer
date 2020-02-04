import copy

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from model.settings import Settings

import config
import utils

class SettingsDialog(QDialog):

    _columnRegex = QRegExp("[A-Z]|([0-9]+)")

    def __init__(self, defaultSettings, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.defaultSettings = defaultSettings
        self.initUI()
        self._validate()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.initCSVSettings())
        layout.addWidget(self.initErrorSettings())
        layout.addWidget(self.initButtons())
        self.setLayout(layout)

    def initErrorSettings(self):
        defaults = self.defaultSettings

        self.rimAgeSigmasRB, self.rimAgeTypeRB, rimAgeLayout = self.createErrorRow(defaults.rimAgeErrorSigmas, defaults.rimAgeErrorType)
        self.mixedPointSigmasRB, self.mixedPointTypeRB, mixedPointLayout = self.createErrorRow(defaults.mixedPointErrorSigmas, defaults.mixedPointErrorType)
        self.outputSigmasRB, self.outputTypeRB, outputLayout = self.createErrorRow(defaults.outputErrorSigmas, defaults.outputErrorType)

        box = QGroupBox("Errors")
        layout = QFormLayout()
        layout.addRow("Rim age", rimAgeLayout)
        layout.addRow("Mixed point ratios", mixedPointLayout)
        layout.addRow("Output", outputLayout)
        box.setLayout(layout)
        return box

    def initCSVSettings(self):
        defaults = self.defaultSettings

        self.rimAgeColumnEntry, self.rimAgeErrorColumnEntry, rimAgeColumnLayout = self.createColumnRow(defaults.rimAgeColumn, defaults.rimAgeErrorColumn)
        self.uPbColumnEntry, self.uPbErrorColumnEntry, uPbColumnLayout = self.createColumnRow(defaults.mixedPointUPbColumn, defaults.mixedPointUPbErrorColumn)
        self.pbPbColumnEntry, self.pbPbErrorColumnEntry, pbPbColumnLayout = self.createColumnRow(defaults.mixedPointPbPbColumn, defaults.mixedPointPbPbErrorColumn)
        
        self.delimiterEntry = QLineEdit(defaults.delimiter)
        self.delimiterEntry.textChanged.connect(self._validate)
        self.delimiterEntry.setFixedWidth(30)
        self.delimiterEntry.setAlignment(Qt.AlignCenter)

        self.hasHeadersCB = QCheckBox()
        self.hasHeadersCB.setChecked(defaults.hasHeaders)
        self.hasHeadersCB.stateChanged.connect(self._validate)

        box = QGroupBox("CSV layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Has headers"), self.hasHeadersCB)
        layout.addRow(QLabel("Column delimiter"), self.delimiterEntry)
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("Columns"))
        layout.addRow(QLabel('Rim age'),rimAgeColumnLayout)
        layout.addRow(QLabel(utils.U_PB_STR), uPbColumnLayout)
        layout.addRow(QLabel(utils.PB_PB_STR),pbPbColumnLayout)
        box.setLayout(layout)
        return box

    def initButtons(self):
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.okButton.setEnabled(False)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)
        widget.setLayout(layout)
        return widget

    def createRadioButtons(self, options, default=0, expanding=True):
        group = QButtonGroup()
        layout = QHBoxLayout()
        for i, option in enumerate(options):
            button = QRadioButton(option)
            button.setChecked(option == default)
            layout.addWidget(button)
            group.addButton(button, i)
        group.buttonReleased.connect(self._validate)
        return group, layout

    def createErrorRow(self, defaultSigmas, defaultType):
        sigmaDefault = utils.get_error_sigmas_str(defaultSigmas)
        sigmasRB, sigmasRBLayout = self.createRadioButtons(utils.SIGMA_OPTIONS_STR, sigmaDefault)
        typeRB, typeRBLayout = self.createRadioButtons(utils.ERROR_TYPE_OPTIONS, defaultType)

        layout = QHBoxLayout()
        layout.addSpacing(20)
        layout.addLayout(typeRBLayout)
        layout.addSpacing(30)
        layout.addLayout(sigmasRBLayout)
        layout.addStretch(0)
        return sigmasRB, typeRB, layout

    def createColumnRow(self, defaultColumn, defaultErrorColumn):
        width = 30

        layout = QHBoxLayout()

        mainValueBox = QLineEdit(defaultColumn)
        mainValueBox.setFixedWidth(width)
        mainValueBox.setAlignment(Qt.AlignCenter)
        self.attachValidator(mainValueBox, self._columnRegex)
        mainValueBox.textChanged.connect(self._validate)

        errorLabel = QLabel("Error")
        errorValueBox = QLineEdit(defaultErrorColumn)
        errorValueBox.setFixedWidth(width)
        errorValueBox.setAlignment(Qt.AlignCenter)
        self.attachValidator(errorValueBox, self._columnRegex)
        errorValueBox.textChanged.connect(self._validate)

        layout.addWidget(mainValueBox)
        layout.addSpacing(20)
        layout.addWidget(errorLabel)
        layout.addWidget(errorValueBox)
        layout.addStretch(0)

        return mainValueBox, errorValueBox, layout

    def attachValidator(self, widget, regex):
        validator = QRegExpValidator(regex)
        widget.setValidator(validator)

    def _validate(self):
        settings = Settings()
        settings.delimiter = self.delimiterEntry.text()
        settings.hasHeaders = self.hasHeadersCB.isChecked()

        settings.rimAgeColumn = self.rimAgeColumnEntry.text()
        settings.rimAgeErrorColumn = self.rimAgeErrorColumnEntry.text()
        settings.mixedPointUPbColumn = self.uPbColumnEntry.text()
        settings.mixedPointUPbErrorColumn = self.uPbErrorColumnEntry.text()
        settings.mixedPointPbPbColumn = self.pbPbColumnEntry.text()
        settings.mixedPointPbPbErrorColumn = self.pbPbErrorColumnEntry.text()

        settings.rimAgeErrorSigmas = utils.SIGMA_OPTIONS[self.rimAgeSigmasRB.checkedId()]
        settings.rimAgeErrorType = utils.ERROR_TYPE_OPTIONS[self.rimAgeTypeRB.checkedId()]
        settings.mixedPointErrorSigmas = utils.SIGMA_OPTIONS[self.mixedPointSigmasRB.checkedId()]
        settings.mixedPointErrorType = utils.ERROR_TYPE_OPTIONS[self.mixedPointTypeRB.checkedId()]
        settings.outputErrorSigmas = utils.SIGMA_OPTIONS[self.outputSigmasRB.checkedId()]
        settings.outputErrorType = utils.ERROR_TYPE_OPTIONS[self.outputTypeRB.checkedId()]

        error = settings.validate()
        self.okButton.setEnabled(error is None)
        self.settings = settings