import utils
from tabs.type import TabType, SettingsType


class UnmixCalculationSettings():
    KEY = (TabType.UNMIX, SettingsType.CALCULATION)

    def __init__(self):
        super().__init__()

        self.outputErrorSigmas = 2
        self.outputErrorType = "Absolute"

    def getOutputErrorStr(self):
        return utils.get_error_str(self.outputErrorSigmas, self.outputErrorType)

    def getOutputError(self, value, diff):
        if self.outputErrorType == "Absolute":
            return diff
        return (diff / value) * 100.0

    @staticmethod
    def _getHeaders(outputErrorSigmas, outputErrorType):
        outputErrorStr = utils.get_error_str(outputErrorSigmas, outputErrorType)

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

    def getHeaders(self):
        return UnmixCalculationSettings._getHeaders(self.outputErrorSigmas, self.outputErrorType)

    @staticmethod
    def getDefaultHeaders():
        return UnmixCalculationSettings._getHeaders(2, "Absolute")

    def validate(self):
        return None