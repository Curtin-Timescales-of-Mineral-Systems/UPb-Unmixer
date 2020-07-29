import pickle
from os import path

from model.settings.type import SettingsType
from utils import stringUtils, config
from model.settings.exports import UnmixExportSettings
from model.settings.imports import UnmixImportSettings
from model.settings.calculation import UnmixCalculationSettings


class Settings:
    __instance = None
    __currentFile = None

    def __init__(self):
        self.perFileSettings = {}
        self.version = config.VERSION

    def __ensureCompatibility(self):
        pass

    @classmethod
    def setCurrentFile(cls, file):
        cls.__currentFile = file
        cls.__ensureInstance()
        if file not in cls.__instance.perFileSettings:
            cls.__instance.perFileSettings[file] = {
                SettingsType.IMPORT: UnmixImportSettings(),
                SettingsType.CALCULATION: UnmixCalculationSettings(),
                SettingsType.EXPORT: UnmixExportSettings()
            }

    @classmethod
    def get(cls, settingsType):
        cls.__ensureInstance()
        perFileSettings = cls.__instance.perFileSettings
        return perFileSettings[cls.__currentFile][settingsType]

    @classmethod
    def update(cls, newSettings):
        cls.__ensureInstance()
        cls.__instance.perFileSettings[cls.__currentFile][newSettings.KEY] = newSettings
        cls.__instance.__save()

    @classmethod
    def __ensureInstance(cls):
        if cls.__instance is None:
            cls.__instance = Settings()
            loadedInstance = cls.load()
            for file, perFileSettings in loadedInstance.perFileSettings.items():
                cls.__instance.perFileSettings[file] = perFileSettings
        return cls.__instance

    def __save(self):
        with open(stringUtils.SAVE_FILE, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        if path.exists(stringUtils.SAVE_FILE):
            with open(stringUtils.SAVE_FILE, 'rb') as inputFile:
                try:
                    result = pickle.load(inputFile)
                    result.__ensureCompatibility()
                    return result
                except Exception as e:
                    print(e)

        return Settings()
