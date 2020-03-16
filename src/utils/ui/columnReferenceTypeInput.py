from utils.csvUtils import ColumnReferenceType
from utils.ui.radioButtonGroup import RadioButtonGroup


class ColumnReferenceTypeInput(RadioButtonGroup):

    def __init__(self, validation):
        super().__init__([e.value for e in ColumnReferenceType], validation, ColumnReferenceType.LETTERS.value)

    def getSelection(self):
        string = super().getSelection()
        return ColumnReferenceType(string)