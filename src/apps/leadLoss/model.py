from enum import Enum

from apps.leadLoss import processing

from apps.abstract.model import AbstractRow, ColumnSpec, AbstractModel
from apps.leadLoss.settings.calculation import LeadLossCalculationSettings


class Column(Enum):
    U_PB_VALUE = 0
    U_PB_ERROR = 1
    PB_PB_VALUE = 2
    PB_PB_ERROR = 3

class LeadLossModel(AbstractModel):

    ####################
    ## Static methods ##
    ####################

    @staticmethod
    def getImportedColumnSpecs():
        return [
            ColumnSpec(Column.U_PB_VALUE),
            ColumnSpec(Column.U_PB_ERROR),
            ColumnSpec(Column.PB_PB_VALUE),
            ColumnSpec(Column.PB_PB_ERROR),
        ]

    @staticmethod
    def getCalculatedColumnSpecs():
        return [
            ColumnSpec("% discordance"),
            ColumnSpec("Age (Ma)")
        ]

    #################
    ## Constructor ##
    #################

    def __init__(self, view):
        super().__init__()

        self.view = view
        self.headers = []
        self.rows = []
        self.concordantRows = []
        self.discordantRows = []

        self.statistics = {}
        self.reconstructedAges = {}

    def loadRawData(self, importSettings, rawHeaders, rawRows):
        self.headers = rawHeaders
        self.rows = [Row(row, importSettings) for row in rawRows]

        importHeaders = importSettings.getHeaders()
        calculationHeaders = LeadLossCalculationSettings.getDefaultHeaders()
        headers = importHeaders + calculationHeaders

        self.view.onHeadersUpdated(headers)
        self.view.onAllRowsUpdated(self.rows)

    def getProcessingFunction(self):
        return processing.process

    def getProcessingData(self):
        return self.rows

    def addProcessingOutput(self, output):
        self.statistics = {}
        self.reconstructedAges = {}
        for rimAge, reconstructedAges, statistic in output[0]:
            self.statistics[rimAge] = statistic
            self.reconstructedAges[rimAge] = reconstructedAges

        concordantAges = [row.calculatedCells[1].value for row in self.rows if row.concordant]
        discordantAges = [row.calculatedCells[1].value for row in self.rows if not row.concordant]
        self.view.onNewlyClassifiedPoints(self.rows, concordantAges, discordantAges)
        self.view.onNewStatistics(self.statistics)

    def selectAgeToCompare(self, targetRimAge):
        if not self.statistics:
            return

        if targetRimAge is not None:
            chosenRimAge = min(self.statistics, key=lambda a: abs(a-targetRimAge))
        else:
            chosenRimAge = max(self.statistics, key=lambda a: self.statistics[a])

        agesToCompare = []
        for reconstructedAge in self.reconstructedAges[chosenRimAge]:
            if reconstructedAge is not None:
                agesToCompare.append(reconstructedAge.values[0])
        self.view.displayAgeComparison(chosenRimAge, agesToCompare)


class Row(AbstractRow):
    def __init__(self, importedValues, importSettings):
        super().__init__(importedValues, importSettings, LeadLossModel.getCalculatedColumnSpecs())

    def uPbValue(self):
        return self.importedCellsByCol[Column.U_PB_VALUE].value

    def pbPbValue(self):
        return self.importedCellsByCol[Column.U_PB_VALUE].value

