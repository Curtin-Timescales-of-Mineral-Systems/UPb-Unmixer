from utils import stringUtils
from model.settings.type import SettingsType


class UnmixCalculationSettings:

    KEY = SettingsType.CALCULATION

    @staticmethod
    def getCalculatedColumnHeaders():
        return [
            "reconstructedAge",
            "reconstructedAgeMin",
            "reconstructedAgeMax",
            "reconstructedUPb",
            "reconstructedUPbMin",
            "reconstructedUPbMax",
            "reconstructedPbPb",
            "reconstructedPbPbMin",
            "reconstructedPbPbMax",
            "metamictScore",
            "precisionScore",
            "rimToCoreScore",
            "totalScore",
        ]

    def __init__(self):
        super().__init__()

        self.outputErrorSigmas = 2
        self.outputErrorType = "Absolute"

    def getOutputErrorStr(self):
        return stringUtils.get_error_str(self.outputErrorSigmas, self.outputErrorType)

    def getOutputError(self, value, diff):
        if self.outputErrorType == "Absolute":
            return diff
        return (diff / value) * 100.0

    @staticmethod
    def _getHeaders(outputErrorSigmas, outputErrorType, useSuperscripts):
        error = str(outputErrorSigmas) + " sigmas"
        minusError = "-" + error
        plusError = "+" + error

        return [
            "Reconstructed age (Ma)",
            minusError,
            plusError,
            "Reconstructed " + stringUtils.getUPbStr(useSuperscripts),
            minusError,
            plusError,
            "Reconstructed " + stringUtils.getPbPbStr(useSuperscripts),
            minusError,
            plusError,
            "Metamict score",
            "Precision score",
            "Core:rim score",
            "Total score",
        ]

    def getHeaders(self):
        return UnmixCalculationSettings._getHeaders(self.outputErrorSigmas, self.outputErrorType, True)

    @staticmethod
    def getDefaultHeaders():
        return UnmixCalculationSettings._getHeaders(2, "Absolute", True)

    def getExportHeaders(self):
        return UnmixCalculationSettings._getHeaders(self.outputErrorSigmas, self.outputErrorType, False)

    def validate(self):
        return None