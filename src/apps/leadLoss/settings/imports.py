from utils import stringUtils
from apps.abstract.settings.imports import AbstractImportSettings
from apps.leadLoss.model import LeadLossModel

from apps.type import TabType, SettingsType


class LeadLossImportSettings(AbstractImportSettings):

    KEY = (TabType.LEAD_LOSS, SettingsType.IMPORT)

    def __init__(self):
        super().__init__(LeadLossModel.getImportedColumnSpecs())

        self.uPbErrorType = "Absolute"
        self.uPbErrorSigmas = 2

        self.pbPbErrorType = "Absolute"
        self.pbPbErrorSigmas = 2

        self.discordanceThreshold = 0.1

    def getUPbErrorStr(self):
        return stringUtils.get_error_str(self.uPbErrorSigmas, self.uPbErrorType)

    def getPbPbErrorStr(self):
        return stringUtils.get_error_str(self.pbPbErrorSigmas, self.pbPbErrorType)

    def getHeaders(self):
        return [
            stringUtils.U_PB_STR,
            "±" + self.getUPbErrorStr(),
            stringUtils.PB_PB_STR,
            "±" + self.getPbPbErrorStr()
        ]

    def validate(self):
        return super().validate()

