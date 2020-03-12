from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit

from utils import stringUtils, csvUtils
from utils.csvUtils import ColumnReferenceType
from utils.ui import uiUtils
from utils.ui.radioButtonGroup import RadioButtonGroup


class ColumnReferenceTypeInput(RadioButtonGroup):

    def __init__(self, validation):
        super().__init__([e.value for e in ColumnReferenceType], validation, ColumnReferenceType.LETTERS.value)

    def getSelection(self):
        string = super().getSelection()
        return ColumnReferenceType(string)


class ColumnReferenceInput(QLineEdit):
    width = 30

    def __init__(self, validation, referenceType, defaultValue):
        super().__init__(defaultValue)
        self.setFixedWidth(self.width)
        self.setAlignment(Qt.AlignCenter)
        self.textChanged.connect(validation)
        self.currentReferenceType = referenceType
        regex = csvUtils.COLUMN_REFERENCE_TYPE_REGEXES[referenceType]
        uiUtils.attachValidator(self, regex)

    def changeColumnReferenceType(self, newReferenceType):
        if self.currentReferenceType == newReferenceType:
            return

        oldText = self.text()
        if self.currentReferenceType is ColumnReferenceType.LETTERS:
            newText = str(csvUtils.columnLettersToNumber(oldText, zeroIndexed=False))
        else:
            newText = csvUtils.columnNumberToLetters(int(oldText), zeroIndexed=False)
        self.setText(newText)

        regex = csvUtils.COLUMN_REFERENCE_TYPE_REGEXES[newReferenceType]
        uiUtils.attachValidator(self, regex)

        self.currentReferenceType = newReferenceType
