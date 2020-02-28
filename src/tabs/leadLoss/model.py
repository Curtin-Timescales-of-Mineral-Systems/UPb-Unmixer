from enum import Enum

from model import errors, calculations

from scipy import stats

from tabs.abstract.abstractModel import AbstractRow, ColumnSpec, CalculatedCell, UncalculatedCell, AbstractModel
from tabs.leadLoss.settings.calculation import LeadLossCalculationSettings


class Column(Enum):
    U_PB = 0
    U_PB_ERROR = 1
    PB_PB = 2
    PB_PB_ERROR = 3

class LeadLossModel(AbstractModel):

    ####################
    ## Static methods ##
    ####################

    @staticmethod
    def getImportedColumnSpecs():
        return [
            ColumnSpec(Column.U_PB),
            ColumnSpec(Column.U_PB_ERROR),
            ColumnSpec(Column.PB_PB),
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

    def process(self, signals, importSettings, calculationSettings):

        # Calculate concordance
        concordantRows = []
        discordantRows = []
        for row in self.rows:
            uPb = row.importedCellsByCol[Column.U_PB].value
            pbPb = row.importedCellsByCol[Column.PB_PB].value
            discordance = calculations.discordance(uPb, pbPb)

            row.calculatedCells[0] = CalculatedCell(discordance)
            row.concordant = discordance < calculationSettings.discordancePercentageCutoff
            if row.concordant:
                age = calculations.concordant_age(uPb, pbPb)
                row.calculatedCells[1] = CalculatedCell(age)
                concordantRows.append(row)
            else:
                row.calculatedCells[1] = UncalculatedCell()
                discordantRows.append(row)

        concordantAges = [row.calculatedCells[1].value for row in concordantRows]

        # Pre-calculate the ufloats as that's the expensive bit
        progressSplit = 1.0
        for i, row in enumerate(self.rows):
            if signals.halt():
                signals.cancelled()
                return

            if not row.concordant:
                uPb = row.importedCellsByCol[Column.U_PB].value
                uPbError = row.importedCellsByCol[Column.U_PB_ERROR].value
                pbPb = row.importedCellsByCol[Column.PB_PB].value
                pbPbError = row.importedCellsByCol[Column.PB_PB_ERROR].value

                row.uPb = errors.ufloat(uPb, uPbError)
                row.pbPb = errors.ufloat(pbPb, pbPbError)

            progress = progressSplit*(i + 1)/len(self.rows)
            signals.progress(progress, i, row)

        # Actually compute the age distributions and statistics
        minAge = 500 * (10 ** 6)
        maxAge = 5000 * (10 ** 6)
        agePoints = 91
        cap = 10

        outputs = []
        for i in range(agePoints):
            rimAge = minAge + i*((maxAge - minAge)/(agePoints - 1))
            rimUPb = calculations.u238pb206_from_age(rimAge)
            rimPbPb = calculations.pb207pb206_from_age(rimAge)

            discordantAges = []
            for j, row in enumerate(self.rows):
                if signals.halt():
                    signals.cancelled()
                    return

                if row.concordant or j >= cap:
                    reconstructedAge = None
                else:
                    reconstructedAge = calculations.discordant_age(rimUPb, rimPbPb, row.uPb, row.pbPb, 1)
                discordantAges.append(reconstructedAge)

            statistic = self.calculateStatistics(concordantAges, discordantAges)
            outputs.append((rimAge, discordantAges, statistic))

            progress = progressSplit + (1 - progressSplit) * (i+i/agePoints)
            #signals.progress(progress)

        signals.completed(outputs)

    def calculateStatistics(self, concordantAges, reconstructedAges):
        discordantAges = []
        for reconstructedAge in reconstructedAges:
            if reconstructedAge is not None and reconstructedAge.hasValue():
                discordantAges.append(reconstructedAge.values[0])

        if not discordantAges or not concordantAges:
            return 0

        pValue = stats.ks_2samp(concordantAges, discordantAges)[1]
        print(pValue)
        return pValue

    def addProcessingOutput(self, output):
        self.statistics = {}
        self.reconstructedAges = {}
        for rimAge, reconstructedAges, statistic in output[0]:
            self.statistics[rimAge] = statistic
            self.reconstructedAges[rimAge] = reconstructedAges

        concordantAges = [row.calculatedCells[1].value for row in self.rows if row.concordant]
        self.view.onNewConcordantPoints(self.rows, concordantAges)
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
            if reconstructedAge is not None and reconstructedAge.hasValue():
                agesToCompare.append(reconstructedAge.values[0])
        self.view.displayAgeComparison(chosenRimAge, agesToCompare)

class Row(AbstractRow):
    def __init__(self, importedValues, importSettings):
        super().__init__(importedValues, importSettings, LeadLossModel.getCalculatedColumnSpecs())

        """
        self.uPbValue = float(importedValues[importSettings.getUPbColumn()])
        self.uPbError = float(importedValues[importSettings.getUPbErrorColumn()])
        self.pbPbValue = float(importedValues[importSettings.getPbPbColumn()])
        self.pbPbError = float(importedValues[importSettings.getPbPbErrorColumn()])

        self.discordance = calculations.discordance(self.uPbValue, self.pbPbValue)
        self.concordant = self.discordance <= importSettings.discordanceThreshold
        if self.concordant:
            self.estimatedAge = calculations.concordant_age(self.uPbValue, self.pbPbValue)
        else:
            self.estimatedAge = None
        """

    """
    def getDisplayValues(self):
        columns = Settings.get(TabType.LEAD_LOSS, SettingsType.IMPORT).getPrimaryDataColumns()
        inputValues = [self.values[i] for i in columns]
        outputValues = [
            self.discordance * 100,
            "" if not self.concordant else self.estimatedAge / (10**6)
        ]
        values = inputValues + outputValues
        roundedValues = [str(utils.round_to_sf(v, 3)) for v in values]
        return roundedValues
    """