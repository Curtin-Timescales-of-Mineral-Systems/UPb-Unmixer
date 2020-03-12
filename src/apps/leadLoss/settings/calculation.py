
from apps.type import TabType, SettingsType


class LeadLossCalculationSettings():

    KEY = (TabType.LEAD_LOSS, SettingsType.CALCULATION)

    def __init__(self):
        self.discordanceType = "Percentages"
        self.discordancePercentageCutoff = 0.1


    def validate(self):
        if self.discordanceType == "Percentages":
            if self.discordancePercentageCutoff < 0 or self.discordancePercentageCutoff > 1.0:
                return "Discordance percentage cutoff must be between 0 and 100%"

        return None

    def getHeaders(self):
        return LeadLossCalculationSettings.getDefaultHeaders()

    @staticmethod
    def getDefaultHeaders():
        return [
            "Discordance (%)",
            "Age (Ma)"
        ]