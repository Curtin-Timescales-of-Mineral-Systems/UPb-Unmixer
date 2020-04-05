from model.column import Column
from model.columnSpec import ColumnSpec
from utils import stringUtils, csvUtils

from model.settings.type import SettingsType
from utils.csvUtils import ColumnReferenceType


class UnmixImportSettings:

    KEY = SettingsType.IMPORT

    @staticmethod
    def getImportedColumnSpecs():
        return [
            ColumnSpec(Column.RIM_AGE_VALUE),
            ColumnSpec(Column.RIM_AGE_ERROR),
            ColumnSpec(Column.MIXED_U_PB_VALUE),
            ColumnSpec(Column.MIXED_U_PB_ERROR),
            ColumnSpec(Column.MIXED_PB_PB_VALUE),
            ColumnSpec(Column.MIXED_PB_PB_ERROR)
        ]

    def __init__(self):
        self.delimiter = ","
        self.hasHeaders = True
        self.columnReferenceType = ColumnReferenceType.LETTERS
        self._columnRefs = {spec.name: i for i, spec in enumerate(self.getImportedColumnSpecs())}

        self.rimAgeErrorType = "Absolute"
        self.rimAgeErrorSigmas = 2

        self.mixedUPbErrorType = "Absolute"
        self.mixedUPbErrorSigmas = 2

        self.mixedPbPbErrorType = "Absolute"
        self.mixedPbPbErrorSigmas = 2

    def getDisplayColumns(self):
        numbers = list(self._columnRefs.values())
        numbers.sort()
        return numbers

    def getDisplayColumnsWithRefs(self):
        numbers = [(col, csvUtils.columnLettersToNumber(colRef, zeroIndexed=True)) for col, colRef in
                   self._columnRefs.items()]
        numbers.sort(key=lambda v: v[0].value)
        return numbers

    def getDisplayColumnsByRefs(self):
        return self._columnRefs


    ## Error getters ##

    def getRimAgeErrorStr(self):
        return stringUtils.get_error_str(self.rimAgeErrorSigmas, self.rimAgeErrorType)

    def getMixedUPbErrorStr(self):
        return stringUtils.get_error_str(self.mixedUPbErrorSigmas, self.mixedUPbErrorType)

    def getMixedPbPbErrorStr(self):
        return stringUtils.get_error_str(self.mixedPbPbErrorSigmas, self.mixedPbPbErrorType)

    ## Headers ##

    def getHeaders(self):
        return [
            "Rim age (Ma)",
            "±" + self.getRimAgeErrorStr(),
            "Mixed " + stringUtils.U_PB_STR,
            "±" + self.getMixedUPbErrorStr(),
            "Mixed " + stringUtils.PB_PB_STR,
            "±" + self.getMixedPbPbErrorStr()
        ]

    ## Validation ##


    def validate(self):
        if not all([v is not None for v in self._columnRefs.values()]):
            return "Must enter a value for each column"

        displayColumns = self.getDisplayColumns()
        if len(set(displayColumns)) != len(displayColumns):
            return "Columns should not contain duplicates"

        return None
