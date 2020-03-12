
from apps.type import TabType, SettingsType

class LeadLossExportSettings():

    KEY = (TabType.LEAD_LOSS, SettingsType.EXPORT)

    def __init__(self):
        outputSF = 3
