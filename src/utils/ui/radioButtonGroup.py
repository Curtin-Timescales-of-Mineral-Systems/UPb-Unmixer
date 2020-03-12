from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QButtonGroup, QHBoxLayout, QRadioButton

from utils.ui import uiUtils


class RadioButtonGroup(QWidget):

    def __init__(self, options, validation, default=0):
        super().__init__()

        self.options = options
        self.group = QButtonGroup()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        for i, option in enumerate(options):
            button = QRadioButton(option)
            button.option = option
            button.setChecked(option == default)
            layout.addWidget(button)
            self.group.addButton(button, i)
        self.group.buttonReleased.connect(validation)

        self.setLayout(layout)

    def getSelection(self):
        return self.options[self.group.checkedId()]