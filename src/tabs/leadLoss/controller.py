from model.async import UFloatAsyncTask, AsyncTask
from model.settings import Settings
from tabs.abstract.controller import AbstractTabController
from tabs.leadLoss.model import LeadLossModel
from tabs.leadLoss.view import LeadLossView
from tabs.type import TabType, SettingsType


class LeadLossTabController(AbstractTabController):

    def __init__(self, application):
        super().__init__(TabType.LEAD_LOSS, application)
        self.name = "Pb loss"
        self.view = LeadLossView(self)
        self.model = LeadLossModel(self.view)

        self.cheatLoad()

    ################
    ## Processing ##
    ################
    """
    def startUFloatGeneration(self):
        ufloatInputs = []
        for row in self.model.rows:
            ufloatInputs.append((row.uPbValue, row.uPbError))
            ufloatInputs.append((row.pbPbValue, row.pbPbError))

        self.signals.progress.connect(self.onUFloatGenerationProgress)
        self.signals.completed.connect(self.onUFloatGenerationEnd)

        self.worker = UFloatAsyncTask(self.signals, ufloatInputs)
        self.worker.start()

    def onUFloatGenerationProgress(self, progress):
        super().onProcessingProgress(progress*0.8)

    def onUFloatGenerationEnd(self, outputs):
        for i, row in enumerate(self.model.rows):
            row.uPb = outputs[2*i]
            row.pbPb = outputs[2*i + 1]

        self.signals.progress.disconnect(self.onUFloatGenerationProgress)
        self.signals.completed.disconnect(self.onUFloatGenerationEnd)

        self.startNumericProcessing()
    """

    def onProcessingProgress(self, progressArgs):
        progress, i, row = progressArgs
        self.model.updateRow(i, row)
        self.view.onProcessingProgress(progress, i, row)

    def selectAgeToCompare(self, age):
        self.model.selectAgeToCompare(age)

    ###########
    ## Other ##
    ###########

    def cheatLoad(self):
        inputFile = "/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests/leadLossTest2.csv"
        self._importCSV(inputFile, Settings.get(TabType.LEAD_LOSS, SettingsType.IMPORT))