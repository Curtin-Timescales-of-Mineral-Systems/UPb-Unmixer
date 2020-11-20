from PyQt5.QtWidgets import QWidget, QGridLayout, QRadioButton, QButtonGroup

from utils import string


class ErrorTypeInput(QWidget):

    def __init__(self, validation, defaultType, defaultSigmas):
        super().__init__()
        layout = QGridLayout()
        layout.setContentsMargins(5,4,0,0)

        self._typeGroup = QButtonGroup()
        for i, option in enumerate(string.ERROR_TYPE_OPTIONS):
            button = QRadioButton(option)
            button.option = option
            button.setChecked(option == defaultType)
            self._typeGroup.addButton(button, i)
            layout.addWidget(button, 0, i)
        self._typeGroup.buttonReleased.connect(validation)

        self._sigmasGroup = QButtonGroup()
        for i, option in enumerate(string.ERROR_SIGMA_OPTIONS):
            button = QRadioButton(string.get_error_sigmas_str(option))
            button.option = option
            button.setChecked(option == defaultSigmas)
            self._sigmasGroup.addButton(button, i)
            layout.addWidget(button, 1, i)
        self._sigmasGroup.buttonReleased.connect(validation)

        self.setLayout(layout)

    def getErrorType(self):
        return string.ERROR_TYPE_OPTIONS[self._typeGroup.checkedId()]

    def getErrorSigmas(self):
        return string.ERROR_SIGMA_OPTIONS[self._sigmasGroup.checkedId()]