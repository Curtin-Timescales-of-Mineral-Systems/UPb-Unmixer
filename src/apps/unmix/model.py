from enum import Enum

from utils import errorUtils, stringUtils, calculations
from apps.abstract.model import AbstractRow, ColumnSpec, CalculatedCell, AbstractModel, UncalculatedCell
from apps.unmix.settings.calculation import UnmixCalculationSettings


class Column(Enum):
    RIM_AGE_VALUE = 0
    RIM_AGE_ERROR = 1
    MIXED_U_PB_VALUE = 2
    MIXED_U_PB_ERROR = 3
    MIXED_PB_PB_VALUE = 4
    MIXED_PB_PB_ERROR = 5

class UnmixModel(AbstractModel):

    @staticmethod
    def getImportedColumnSpecs():
        return [
            ColumnSpec(Column.RIM_AGE_VALUE),
            ColumnSpec(Column.RIM_AGE_ERROR),
            ColumnSpec(Column.MIXED_U_PB_VALUE),
            ColumnSpec(Column.MIXED_U_PB_ERROR),
            ColumnSpec(Column.MIXED_PB_PB_VALUE),
            ColumnSpec(Column.MIXED_PB_PB_ERROR)
        ]

    @staticmethod
    def getCalculatedColumnSpecs():
        return [
            ColumnSpec("reconstructedAge"),
            ColumnSpec("reconstructedAgeMin"),
            ColumnSpec("reconstructedAgeMax"),
            ColumnSpec("reconstructedUPb"),
            ColumnSpec("reconstructedUPbMin"),
            ColumnSpec("reconstructedUPbMax"),
            ColumnSpec("reconstructedPbPb"),
            ColumnSpec("reconstructedPbPbMin"),
            ColumnSpec("reconstructedPbPbMax"),
        ]


    def __init__(self, view):
        super().__init__()
        self.rows = None
        self.view = view

    def loadRawData(self, importSettings, rawHeaders, rawRows):
        self.rawHeaders = rawHeaders
        self.rows = [Row(row, importSettings) for row in rawRows]

        importHeaders = importSettings.getHeaders()
        calculationHeaders = UnmixCalculationSettings.getDefaultHeaders()
        headers = importHeaders + calculationHeaders

        self.view.onHeadersUpdated(headers)
        self.view.onAllRowsUpdated(self.rows)

    def getProcessingFunction(self):
        return process

    def getProcessingData(self):
        return self.rows

    def addProcessingOutput(self, *args):
        pass

    def getExportData(self, calculationSettings):
        headers = self.rawHeaders + calculationSettings.getExportHeaders()
        rows = [row.rawImportedValues + [cell.value for cell in row.calculatedCells] for row in self.rows]
        return headers, rows


def process(signals, rows, importSettings, calculationSettings):
    for i, row in enumerate(rows):
        if signals.halt():
            signals.cancelled()
            return
        row.process(importSettings, calculationSettings)
        signals.progress((i+1)/len(rows), i, row)
    signals.completed(None)

class Row(AbstractRow):
    def __init__(self, importedValues, importSettings):
        super().__init__(importedValues, importSettings, UnmixModel.getCalculatedColumnSpecs())

        self.processed = False
        self.validOutput = False

    def process(self, importSettings, calculationSettings):
        self.processed = True

        if not self.validImports:
            self.calculatedCells = [CalculatedCell(None) for _ in range(9)]
            return

        self.rimAgeValue = self.importedCellsByCol[Column.RIM_AGE_VALUE].value
        self.rimAgeRawError = self.importedCellsByCol[Column.RIM_AGE_ERROR].value
        self.rimAgeStDev = calculations.convert_to_stddev(
            self.rimAgeValue,
            self.rimAgeRawError,
            importSettings.rimAgeErrorType,
            importSettings.rimAgeErrorSigmas
        )
        rimAge = errorUtils.ufloat(self.rimAgeValue, self.rimAgeStDev) * 10 ** 6

        self.mixedUPbValue = self.importedCellsByCol[Column.MIXED_U_PB_VALUE].value
        self.mixedUPbRawError = self.importedCellsByCol[Column.MIXED_U_PB_ERROR].value
        self.mixedUPbStDev = calculations.convert_to_stddev(
            self.mixedUPbValue,
            self.mixedUPbRawError,
            importSettings.mixedUPbErrorType,
            importSettings.mixedUPbErrorSigmas
        )
        mixedUPb = errorUtils.ufloat(self.mixedUPbValue, self.mixedUPbStDev)

        self.mixedPbPbValue = self.importedCellsByCol[Column.MIXED_PB_PB_VALUE].value
        self.mixedPbPbRawError = self.importedCellsByCol[Column.MIXED_PB_PB_ERROR].value
        self.mixedPbPbStDev = calculations.convert_to_stddev(
            self.mixedPbPbValue,
            self.mixedPbPbRawError,
            importSettings.mixedPbPbErrorType,
            importSettings.mixedPbPbErrorSigmas
        )
        mixedPbPb = errorUtils.ufloat(self.mixedPbPbValue, self.mixedPbPbStDev)

        rimUPb = calculations.u238pb206_from_age(rimAge)
        rimPbPb = calculations.pb207pb206_from_age(rimAge)

        self.rimUPbValue = errorUtils.value(rimUPb)
        self.rimUPbStDev = errorUtils.stddev(rimUPb)
        self.rimUPbError = calculations.convert_from_stddev_with_sigmas(
            self.rimUPbValue,
            self.rimUPbStDev,
            calculationSettings.outputErrorType,
            calculationSettings.outputErrorSigmas
        )
        self.rimPbPbValue = errorUtils.value(rimPbPb)
        self.rimPbPbStDev = errorUtils.stddev(rimPbPb)
        self.rimPbPbError = calculations.convert_from_stddev_with_sigmas(
            self.rimPbPbValue,
            self.rimPbPbStDev,
            calculationSettings.outputErrorType,
            calculationSettings.outputErrorSigmas
        )

        self.reconstructedAgeObj = calculations.discordant_age(rimUPb, rimPbPb, mixedUPb, mixedPbPb, calculationSettings.outputErrorSigmas)

        self.validOutput = self.reconstructedAgeObj is not None
        if not self.validOutput:
            return
        self.validOutput = self.reconstructedAgeObj.fullyValid

        t, t_min, t_max = self.reconstructedAgeObj.getAge()
        u, u_min, u_max = self.reconstructedAgeObj.getUPb()
        p, p_min, p_max = self.reconstructedAgeObj.getPbPb()

        def getErrorCell(value, error):
            if error is None:
                return UncalculatedCell()
            else:
                return CalculatedCell(calculationSettings.getOutputError(value, error))

        self.calculatedCells[0] = CalculatedCell(t)
        self.calculatedCells[1] = getErrorCell(t, t_min)
        self.calculatedCells[2] = getErrorCell(t, t_max)

        self.calculatedCells[3] = CalculatedCell(u)
        self.calculatedCells[4] = getErrorCell(u, u_min)
        self.calculatedCells[5] = getErrorCell(u, u_max)

        self.calculatedCells[6] = CalculatedCell(p)
        self.calculatedCells[7] = getErrorCell(p, p_min)
        self.calculatedCells[8] = getErrorCell(p, p_max)