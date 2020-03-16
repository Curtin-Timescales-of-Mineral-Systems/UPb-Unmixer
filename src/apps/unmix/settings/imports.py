from utils import stringUtils

from apps.abstract.settings.imports import AbstractImportSettings
from apps.type import TabType, SettingsType
from apps.unmix.model import UnmixModel

class UnmixImportSettings(AbstractImportSettings):

    KEY = (TabType.UNMIX, SettingsType.IMPORT)

    def __init__(self):
        super().__init__(UnmixModel.getImportedColumnSpecs())

        self.rimAgeErrorType = "Absolute"
        self.rimAgeErrorSigmas = 2

        self.mixedUPbErrorType = "Absolute"
        self.mixedUPbErrorSigmas = 2

        self.mixedPbPbErrorType = "Absolute"
        self.mixedPbPbErrorSigmas = 2

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
        if not all(self._columnRefs.values()):
            return "Must enter a value for each column"

        displayColumns = self.getDisplayColumns()
        if len(set(displayColumns)) != len(displayColumns):
            return "Columns should not contain duplicates"

        self.delimiter = ","

        return None
