import utils
from tabs.abstract.settings.imports import AbstractImportSettings
from tabs.leadLoss.model import LeadLossModel

from tabs.type import TabType, SettingsType


class LeadLossImportSettings(AbstractImportSettings):

    KEY = (TabType.LEAD_LOSS, SettingsType.IMPORT)

    def __init__(self):
        super().__init__(LeadLossModel.getImportedColumnSpecs())

        self.inputErrorSigmas = 2
        self.inputErrorType = "Absolute"

        self.discordanceThreshold = 0.1

    def getInputErrorStr(self):
        return utils.get_error_str(self.inputErrorSigmas, self.inputErrorType)

    def getHeaders(self):
        inputErrorStr = "±" + self.getInputErrorStr()
        return [
            utils.U_PB_STR,
            inputErrorStr,
            utils.PB_PB_STR,
            inputErrorStr
        ]

    def validate(self):
        return None

