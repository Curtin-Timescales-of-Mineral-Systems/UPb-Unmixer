import pickle
from os import path

from model.settings.type import SettingsType
from utils import string, config
from model.settings.exports import ExportSettings
from model.settings.imports import ImportSettings
from model.settings.calculation import CalculationSettings


class Settings:
    __instance = None
    __current_file = None

    def __init__(self):
        self._per_file_settings = {}
        self._version = config.VERSION

    def __ensure_compatibility(self):
        if config.VERSION == "2.0" and self._version != config.VERSION:
            self._per_file_settings = {}

    @classmethod
    def set_current_file(cls, file: str):
        cls.__current_file = file
        cls.__ensure_instance()
        if file not in cls.__instance._per_file_settings:
            cls.__instance._per_file_settings[file] = {
                SettingsType.IMPORT: ImportSettings(),
                SettingsType.CALCULATION: CalculationSettings(),
                SettingsType.EXPORT: ExportSettings()
            }

    @classmethod
    def get(cls, type: SettingsType):
        cls.__ensure_instance()
        per_file_settings = cls.__instance._per_file_settings
        return per_file_settings[cls.__current_file][type]

    @classmethod
    def update(cls, newSettings):
        cls.__ensure_instance()
        cls.__instance._per_file_settings[cls.__current_file][newSettings.KEY] = newSettings
        cls.__instance.__save()

    @classmethod
    def __ensure_instance(cls):
        if cls.__instance is None:
            cls.__instance = Settings()
            loaded_instance = cls.__load()
            for file, per_file_settings in loaded_instance._per_file_settings.items():
                cls.__instance._per_file_settings[file] = per_file_settings
        return cls.__instance

    def __save(self):
        with open(string.SAVE_FILE, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def __load():
        if path.exists(string.SAVE_FILE):
            with open(string.SAVE_FILE, 'rb') as inputFile:
                try:
                    result = pickle.load(inputFile)
                    result.__ensure_compatibility()
                    return result
                except Exception as e:
                    print(e)

        return Settings()
