from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import utils


class StatusBarWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(StatusBarWidget, self).__init__(*args, **kwargs)
        self.initUI()


    def initUI(self):
        self.text = QLabel("No data imported")
        self.icon = QLabel()
        self._setIcon(False)

        self.progressBar = QProgressBar()
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.hide()
        self.progressBar.setRange(0, 100)
        utils.retainSize(self.progressBar)

        layout = QHBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addSpacing(10)
        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

    def startTask(self, text):
        self.progressBar.show()
        self.text.setText(text)
        self.icon.hide()
        self.updateTask(0)

    def updateTask(self, value):
        self.progressBar.setValue(int(value * 100))

    def endTask(self, success, text):
        self.progressBar.hide()
        self.text.setText(text)
        self.text.adjustSize()
        self.icon.show()
        self._setIcon(success)

    def _setIcon(self, success):
        style = "SP_DialogApplyButton" if success else "SP_BrowserStop"
        icon = self.style().standardIcon(getattr(QStyle, style))
        self.icon.setPixmap(icon.pixmap(QSize(20, 20)))