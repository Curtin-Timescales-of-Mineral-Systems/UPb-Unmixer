from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from utils.ui import uiUtils


class AbstractSettingsDialog(QDialog):
    def __init__(self, defaultSettings, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.setModal(True)
        self.defaultSettings = defaultSettings
        self.initUI()
        self.setSizeGripEnabled(False)
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

        layout = QHBoxLayout()
        layout.setSpacing(uiUtils.FORM_HORIZONTAL_SPACING)
        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    ################
    ## Validation ##
    ################

    def _validate(self):
        settings = self._createSettings()
        error = settings.validate()
        self.okButton.setEnabled(error is None)
        self.settings = settings

    def createLabelWithHelp(self, labelText, helpText):

        label = QLabel(labelText)

        icon = self.style().standardIcon(getattr(QStyle, "SP_MessageBoxQuestion"))
        pixmap = icon.pixmap(QSize(20, 20))
        iconLabel = QLabel()
        iconLabel.setPixmap(pixmap)
        iconLabel.setToolTip(helpText)

        layout = QHBoxLayout()
        layout.addWidget(iconLabel)
        layout.addWidget(label)
        layout.setContentsMargins(0,0,0,0)

        widget = QWidget()
        widget.setLayout(layout)
        return widget