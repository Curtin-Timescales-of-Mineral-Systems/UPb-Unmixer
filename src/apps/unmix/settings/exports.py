from apps.abstract.settings.exports import AbstractExportSettings
from apps.type import TabType, SettingsType


class UnmixExportSettings(AbstractExportSettings):
    KEY = (TabType.UNMIX, SettingsType.EXPORT)

