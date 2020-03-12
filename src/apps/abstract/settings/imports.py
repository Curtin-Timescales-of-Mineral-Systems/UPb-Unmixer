from utils import csvUtils
from utils.csvUtils import ColumnReferenceType


class AbstractImportSettings:

    def __init__(self, importColumnSpecs):
        self.delimiter = ","
        self.hasHeaders = True
        self.columnReferenceType = ColumnReferenceType.LETTERS

        self._columnRefs = {spec.type: i for i, spec in enumerate(importColumnSpecs)}

    def getDisplayColumns(self):
        numbers = [(col, csvUtils.columnLettersToNumber(colRef, zeroIndexed=True)) for col, colRef in self._columnRefs.items()]
        numbers.sort(key=lambda v: v[0].value)
        return numbers

    def getDisplayColumnsAsStrings(self):
        return {typ: csvUtils.columnNumberToLetters(ref, zeroIndexed=True) for typ, ref in self._columnRefs.items()}
