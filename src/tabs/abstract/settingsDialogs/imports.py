from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import utils
from tabs.abstract.settingsDialogs.general import AbstractSettingsDialog


class AbstractImportSettingsDialog(AbstractSettingsDialog):
    _columnRegex = QRegExp("[A-Z]|([0-9]+)")

    def __init__(self, defaultSettings, *args, **kwargs):
        super().__init__(defaultSettings, *args, **kwargs)
        self.setWindowTitle("CSV import settings")

    ###############
    ## UI layout ##
    ###############

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.initCSVSettings())
        self.layout.addWidget(self.initErrorSettings())
        self.layout.addWidget(self.initButtons())
        self.setLayout(self.layout)

    ###########
    ## Utils ##
    ###########

    def _createStandardCSVFields(self):
        delimiterEntry = QLineEdit(self.defaultSettings.delimiter)
        delimiterEntry.textChanged.connect(self._validate)
        delimiterEntry.setFixedWidth(30)
        delimiterEntry.setAlignment(Qt.AlignCenter)

        hasHeadersCB = QCheckBox()
        hasHeadersCB.setChecked(self.defaultSettings.hasHeaders)
        hasHeadersCB.stateChanged.connect(self._validate)

        return delimiterEntry, hasHeadersCB

    def _createColumnRow(self, defaultColumn, defaultErrorColumn):
        width = 30

        layout = QHBoxLayout()

        mainValueBox = QLineEdit(defaultColumn)
        mainValueBox.setFixedWidth(width)
        mainValueBox.setAlignment(Qt.AlignCenter)
        self._attachValidator(mainValueBox, self._columnRegex)
        mainValueBox.textChanged.connect(self._validate)

        errorLabel = QLabel("Error")
        errorValueBox = QLineEdit(defaultErrorColumn)
        errorValueBox.setFixedWidth(width)
        errorValueBox.setAlignment(Qt.AlignCenter)
        self._attachValidator(errorValueBox, self._columnRegex)
        errorValueBox.textChanged.connect(self._validate)

        layout.addWidget(mainValueBox)
        layout.addSpacing(20)
        layout.addWidget(errorLabel)
        layout.addWidget(errorValueBox)
        layout.addStretch(0)

        return mainValueBox, errorValueBox, layout
