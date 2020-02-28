from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import utils


class AbstractSettingsDialog(QDialog):
    def __init__(self, defaultSettings, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.setModal(True)
        self.defaultSettings = defaultSettings
        self.initUI()
        self._validate()

    ###############
    ## UI layout ##
    ###############

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

    ###########
    ## Utils ##
    ###########

    def _createRadioButtons(self, options, default=0, expanding=True):
        group = QButtonGroup()
        layout = QHBoxLayout()
        for i, option in enumerate(options):
            button = QRadioButton(option)
            button.setChecked(option == default)
            layout.addWidget(button)
            group.addButton(button, i)
        group.buttonReleased.connect(self._validate)
        return group, layout

    def _createErrorRow(self, defaultSigmas, defaultType):
        sigmaDefault = utils.get_error_sigmas_str(defaultSigmas)
        sigmasRB, sigmasRBLayout = self._createRadioButtons(utils.SIGMA_OPTIONS_STR, sigmaDefault)
        typeRB, typeRBLayout = self._createRadioButtons(utils.ERROR_TYPE_OPTIONS, defaultType)

        layout = QHBoxLayout()
        layout.addSpacing(20)
        layout.addLayout(typeRBLayout)
        layout.addSpacing(30)
        layout.addLayout(sigmasRBLayout)
        layout.addStretch(0)
        return sigmasRB, typeRB, layout

    ################
    ## Validation ##
    ################

    def _attachValidator(self, widget, regex):
        validator = QRegExpValidator(regex)
        widget.setValidator(validator)

    def _validate(self):
        settings = self._createSettings()
        error = settings.validate()
        self.okButton.setEnabled(error is None)
        self.settings = settings
