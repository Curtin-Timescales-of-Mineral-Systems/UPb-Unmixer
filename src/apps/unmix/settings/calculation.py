from utils import stringUtils
from apps.type import TabType, SettingsType


class UnmixCalculationSettings():
    KEY = (TabType.UNMIX, SettingsType.CALCULATION)

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
        outputErrorStr = stringUtils.get_error_str(outputErrorSigmas, outputErrorType)

        return [
            "Reconstructed age (Ma)",
            "-" + outputErrorStr,
            "+" + outputErrorStr,
            "Reconstructed " + stringUtils.getUPbStr(useSuperscripts),
            "-" + outputErrorStr,
            "+" + outputErrorStr,
            "Reconstructed " + stringUtils.getPbPbStr(useSuperscripts),
            "-" + outputErrorStr,
            "+" + outputErrorStr
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