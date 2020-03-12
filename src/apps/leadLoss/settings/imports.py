from utils import stringUtils
from apps.abstract.settings.imports import AbstractImportSettings
from apps.leadLoss.model import LeadLossModel

from apps.type import TabType, SettingsType


class LeadLossImportSettings(AbstractImportSettings):

    KEY = (TabType.LEAD_LOSS, SettingsType.IMPORT)

    def __init__(self):
        super().__init__(LeadLossModel.getImportedColumnSpecs())

        self.inputErrorSigmas = 2
        self.inputErrorType = "Absolute"

        self.discordanceThreshold = 0.1

    def getInputErrorStr(self):
        return stringUtils.get_error_str(self.inputErrorSigmas, self.inputErrorType)

    def getHeaders(self):
        inputErrorStr = "±" + self.getInputErrorStr()
        return [
            stringUtils.U_PB_STR,
            inputErrorStr,
            stringUtils.PB_PB_STR,
            inputErrorStr
        ]

    def validate(self):
        return None

