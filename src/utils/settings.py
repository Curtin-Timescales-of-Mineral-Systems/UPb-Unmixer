import pickle
from os import path

from utils import stringUtils, config
from model.settings.exports import UnmixExportSettings
from model.settings.imports import UnmixImportSettings
from model.settings.calculation import UnmixCalculationSettings


class Settings:
    __instance = None

    def __init__(self):
        self.contents = {
            UnmixImportSettings.KEY: UnmixImportSettings(),
            UnmixCalculationSettings.KEY: UnmixCalculationSettings(),
            UnmixExportSettings.KEY: UnmixExportSettings()
        }
        self.version = config.VERSION

    def ensureCompatibility(self):
        if not hasattr(self, 'version'):
            self.version = "1.0"

        if self.version == "1.0":
            self.contents[UnmixImportSettings.KEY].upgradeToVersion1p1()

    @classmethod
    def get(cls, settingsType):
        cls.__ensureInstance()
        return cls.__instance.contents[settingsType]
        # raise Exception("Unknown tab and settingsDialogs: " + type(tabType) + " " + type(settingsType))]

    @classmethod
    def update(cls, newSettings):
        cls.__ensureInstance()
        cls.__instance.contents[newSettings.KEY] = newSettings
        cls.__instance.__save()

    @classmethod
    def __ensureInstance(cls):
        if cls.__instance is None:
            cls.__instance = Settings()
            loadedInstance = cls.load()
            for key, value in loadedInstance.contents.items():
                cls.__instance.contents[key] = value
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
                    result.ensureCompatibility()
                    return result
                except Exception as e:
                    print(e)

        return Settings()