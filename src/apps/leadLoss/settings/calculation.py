
from apps.type import TabType, SettingsType


class LeadLossCalculationSettings():

    KEY = (TabType.LEAD_LOSS, SettingsType.CALCULATION)

    def __init__(self):
        self.discordanceType = "Percentages"
        self.discordancePercentageCutoff = 0.1
        self.discordanceEllipseSigmas = 2

        self.minimumRimAge = 500
        self.maximumRimAge = 4500
        self.samplingResolution = 100


    def validate(self):
        if self.discordanceType == "Percentages":
            if self.discordancePercentageCutoff < 0 or self.discordancePercentageCutoff > 1.0:
                return "Discordance percentage cutoff must be between 0 and 100%"

        if self.minimumRimAge >= self.maximumRimAge:
            return "The minimum rim age must be strictly less than the maximum rim age"

        if self.samplingResolution <= 0:
            return "The sampling resolution must be strictly greater than 0"

        return None

    def getHeaders(self):
        return LeadLossCalculationSettings.getDefaultHeaders()

    @staticmethod
    def getDefaultHeaders():
        return [
            "Discordance (%)",
            "Age (Ma)"
        ]