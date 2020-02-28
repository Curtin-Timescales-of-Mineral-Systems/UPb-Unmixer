import pickle
from os import path

import utils
from tabs.leadLoss.settings.exports import LeadLossExportSettings
from tabs.leadLoss.settings.imports import LeadLossImportSettings
from tabs.leadLoss.settings.calculation import LeadLossCalculationSettings
from tabs.unmix.settings.exports import UnmixExportSettings
from tabs.unmix.settings.imports import UnmixImportSettings
from tabs.unmix.settings.calculation import UnmixCalculationSettings


class Settings:
    __instance = None

    def __init__(self):
        self.contents = {
            UnmixImportSettings.KEY: UnmixImportSettings(),
            UnmixCalculationSettings.KEY: UnmixCalculationSettings(),
            UnmixExportSettings.KEY: UnmixExportSettings(),

            LeadLossImportSettings.KEY: LeadLossImportSettings(),
            LeadLossCalculationSettings.KEY: LeadLossCalculationSettings(),
            LeadLossExportSettings.KEY: LeadLossExportSettings(),
        }

    @classmethod
    def get(cls, tabType, settingsType):
        cls.__ensureInstance()
        return cls.__instance.contents[(tabType, settingsType)]
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
        with open(utils.SAVE_FILE, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        if path.exists(utils.SAVE_FILE):
            with open(utils.SAVE_FILE, 'rb') as input:
                try:
                    return pickle.load(input)
                except Exception as e:
                    print(e)

        return Settings()
