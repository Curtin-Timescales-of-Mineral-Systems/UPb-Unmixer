from enum import Enum


class TabType(Enum):
    UNMIX = 1
    LEAD_LOSS = 2


class SettingsType(Enum):
    IMPORT = 1
    CALCULATION = 2
    EXPORT = 3
