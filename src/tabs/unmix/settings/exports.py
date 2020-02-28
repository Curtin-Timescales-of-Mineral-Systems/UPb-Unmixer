import utils
from tabs.abstract.settings.exports import AbstractExportSettings
from tabs.type import TabType, SettingsType


class UnmixExportSettings(AbstractExportSettings):
    KEY = (TabType.UNMIX, SettingsType.EXPORT)

