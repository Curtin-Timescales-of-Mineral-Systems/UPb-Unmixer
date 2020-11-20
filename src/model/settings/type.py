from enum import Enum


class SettingsType(Enum):
    """
    The different types of user settings in the application.
    """
    IMPORT = 1
    CALCULATION = 2
    EXPORT = 3
