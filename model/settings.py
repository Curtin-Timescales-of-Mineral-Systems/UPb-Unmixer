import utils
from os import path
import pickle

class Settings:
    def __init__(self):
        self.rimAgeErrorSigmas = 2
        self.rimAgeErrorType = "Absolute"

        self.mixedPointErrorSigmas = 2
        self.mixedPointErrorType = "Absolute"

        self.outputErrorSigmas = 2
        self.outputErrorType = "Absolute"

        self.numericColumns = False
        self.rimAgeColumn = "A"
        self.rimAgeErrorColumn = "B"
        self.mixedPointUPbColumn = "C"
        self.mixedPointUPbErrorColumn = "D"
        self.mixedPointPbPbColumn = "E"
        self.mixedPointPbPbErrorColumn = "F"

        self.delimiter = ","
        self.hasHeaders = True

    ## Error getters ##

    def getRimAgeErrorStr(self):
        return utils.get_error_str(self.rimAgeErrorSigmas, self.rimAgeErrorType)

    def getMixedPointErrorStr(self):
        return utils.get_error_str(self.mixedPointErrorSigmas, self.mixedPointErrorType)

    def getOutputErrorStr(self):
        return utils.get_error_str(self.outputErrorSigmas, self.outputErrorType)

    def getOutputError(self, value, diff):
        if self.outputErrorType == "Absolute":
            return diff
        return (diff/value) * 100.0

    ## Column getters ##

    def _get_column_number(self, column_ref):
        if isinstance(column_ref, int):
            return column_ref
        return ord(column_ref.lower()) - 97

    def getRimAgeColumn(self):
        return self._get_column_number(self.rimAgeColumn)

    def getRimAgeErrorColumn(self):
        return self._get_column_number(self.rimAgeErrorColumn)

    def getMixedPointUPbColumn(self):
        return self._get_column_number(self.mixedPointUPbColumn)

    def getMixedPointUPbErrorColumn(self):
        return self._get_column_number(self.mixedPointUPbErrorColumn)

    def getMixedPointPbPbColumn(self):
        return self._get_column_number(self.mixedPointPbPbColumn)

    def getMixedPointPbPbErrorColumn(self):
        return self._get_column_number(self.mixedPointPbPbErrorColumn)

    def getNumberOfDisplayColumns(self):
        return 15

    def getPrimaryDataColumns(self):
        return [
            self.getRimAgeColumn(),
            self.getRimAgeErrorColumn(),
            self.getMixedPointUPbColumn(),
            self.getMixedPointUPbErrorColumn(),
            self.getMixedPointPbPbColumn(),
            self.getMixedPointPbPbErrorColumn(),
        ]

    def getDisplayColumns(self):
        return self.getPrimaryDataColumns()

    def getInputDataHeaders(self):
        return [
            "Rim age (Ma)",
            "±" + self.getRimAgeErrorStr(),
            "Mixed " + utils.U_PB_STR,
            "±" + self.getMixedPointErrorStr(),
            "Mixed " + utils.PB_PB_STR,
            "±" + self.getMixedPointErrorStr()
        ]

    def getOutputDataHeaders(self):
        outputErrorStr = self.getOutputErrorStr()

        return [
            "Reconstructed age (Ma)",
            "-" + outputErrorStr,
            "+" + outputErrorStr,
            "Reconstructed " + utils.U_PB_STR,
            "-" + outputErrorStr,
            "+" + outputErrorStr,
            "Reconstructed " + utils.PB_PB_STR,
            "-" + outputErrorStr,
            "+" + outputErrorStr
        ]

    def getAllDisplayHeaders(self):
        return self.getInputDataHeaders() + self.getOutputDataHeaders()

    ## Validation ##

    def validate(self):
        rawColumns = [
            self.rimAgeColumn,
            self.rimAgeErrorColumn,
            self.mixedPointUPbColumn,
            self.mixedPointUPbErrorColumn,
            self.mixedPointPbPbColumn,
            self.mixedPointPbPbErrorColumn
        ]
        if not all(rawColumns):
            return "Must enter a value for each column"

        displayColumns = self.getDisplayColumns()
        if len(set(displayColumns)) != len(displayColumns):
            return "Columns should not contain duplicates"

        self.delimiter = ","

        return None

    def save(self):
        with open(utils.SAVE_FILE, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def loadSettings():
        if not path.exists(utils.SAVE_FILE):
            return Settings()

        with open(utils.SAVE_FILE, 'rb') as input:
            return pickle.load(input)