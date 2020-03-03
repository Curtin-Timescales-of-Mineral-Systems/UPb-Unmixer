import csv_mode
from model.async import AsyncPyQTSignals, AsyncTask
from model.settings import Settings
from tabs.type import SettingsType


class AbstractTabController():

    def __init__(self, tabType, application):
        self.tabType = tabType
        self.application = application
        self.worker = None

        self.signals = AsyncPyQTSignals()
        self.signals.started.connect(self.onProcessingStart)
        self.signals.cancelled.connect(self.onProcessingCancelled)
        self.signals.errored.connect(self.onProcessingErrored)

    ############
    ## Import ##
    ############

    def importCSV(self):
        self.inputFile = self.view.getInputFile()
        if not self.inputFile:
            return

        self.view.getSettings(SettingsType.IMPORT, self._importCSVWithSettings)

    def _importCSVWithSettings(self, importSettings):
        if not importSettings:
            return
        Settings.update(importSettings)

        self._importCSV(self.inputFile, importSettings)

    def _importCSV(self, inputFile, importSettings):
        results = csv_mode.read_input(inputFile, importSettings)
        success = results is not None
        if success:
            self.model.loadRawData(importSettings, *results)
        self.view.onCSVImportFinished(success, inputFile)

    #############
    ## Process ##
    #############

    def process(self):
        self.view.getSettings(SettingsType.CALCULATION, self._processWithSettings)

    def _processWithSettings(self, processingSettings):
        if not processingSettings:
            return
        Settings.update(processingSettings)

        importSettings = Settings.get(self.tabType, SettingsType.IMPORT)
        calculationSettings = Settings.get(self.tabType, SettingsType.CALCULATION)
        headers = importSettings.getHeaders() + calculationSettings.getHeaders()
        self.model.resetCalculations()
        self.view.onHeadersUpdated(headers)
        self.view.onAllRowsUpdated(self.model.rows)

        self._process(processingSettings)


    def _process(self, calculationSettings):
        self.signals.progress.connect(self.onProcessingProgress)
        self.signals.completed.connect(self.onProcessingCompleted)

        importSettings = Settings.get(self.tabType, SettingsType.IMPORT)
        self.worker = AsyncTask(self.signals, self.model.process, importSettings, calculationSettings)
        self.worker.start()

    def onProcessingCompleted(self, output):
        self.signals.progress.disconnect(self.onProcessingProgress)
        self.signals.completed.disconnect(self.onProcessingCompleted)
        self.view.onProcessingCompleted()

        self.model.addProcessingOutput(output)

    def cancelProcessing(self):
        if self.worker is not None:
            self.worker.halt()

    ############
    ## Export ##
    ############

    def exportCSV(self):
        pass

    ###########
    ## Utils ##
    ###########

    def onProcessingStart(self):
        self.view.onProcessingStart()

    def onProcessingCancelled(self):
        self.view.onProcessingCancelled()

    def onProcessingErrored(self, exception):
        self.view.onProcessingErrored(exception)