from utils.async import UFloatAsyncTask, AsyncTask
from utils.settings import Settings
from apps.abstract.controller import AbstractTabController
from apps.leadLoss.model import LeadLossModel
from apps.leadLoss.view import LeadLossView
from apps.type import TabType, SettingsType


class LeadLossTabController(AbstractTabController):

    def __init__(self):
        super().__init__(TabType.LEAD_LOSS)
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
        for row in self.utils.rows:
            ufloatInputs.append((row.uPbValue, row.uPbError))
            ufloatInputs.append((row.pbPbValue, row.pbPbError))

        self.signals.progress.connect(self.onUFloatGenerationProgress)
        self.signals.completed.connect(self.onUFloatGenerationEnd)

        self.worker = UFloatAsyncTask(self.signals, ufloatInputs)
        self.worker.start()

    def onUFloatGenerationProgress(self, progress):
        super().onProcessingProgress(progress*0.8)

    def onUFloatGenerationEnd(self, outputs):
        for i, row in enumerate(self.utils.rows):
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