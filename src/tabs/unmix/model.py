from enum import Enum

import utils
from model import errors, calculations
from tabs.abstract.abstractModel import AbstractRow, ColumnSpec, CalculatedCell, AbstractModel
from tabs.unmix.settings.calculation import UnmixCalculationSettings


class Column(Enum):
    RIM_AGE = 0
    RIM_AGE_ERROR = 1
    MIXED_U_PB = 2
    MIXED_U_PB_ERROR = 3
    MIXED_PB_PB = 4
    MIXED_PB_PB_ERROR = 5

class UnmixModel(AbstractModel):

    @staticmethod
    def getImportedColumnSpecs():
        return [
            ColumnSpec(Column.RIM_AGE),
            ColumnSpec(Column.RIM_AGE_ERROR),
            ColumnSpec(Column.MIXED_U_PB),
            ColumnSpec(Column.MIXED_U_PB_ERROR),
            ColumnSpec(Column.MIXED_PB_PB),
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
        self.headers = rawHeaders
        self.rows = [Row(row, importSettings) for row in rawRows]

        importHeaders = importSettings.getHeaders()
        calculationHeaders = UnmixCalculationSettings.getDefaultHeaders()
        headers = importHeaders + calculationHeaders

        self.view.onHeadersUpdated(headers)
        self.view.onAllRowsUpdated(self.rows)

    def process(self, signals, importSettings, calculationSettings):
        for i, row in enumerate(self.rows):
            if signals.halt():
                signals.cancelled()
                return
            row.process(importSettings, calculationSettings)
            signals.progress((i+1)/len(self.rows), i, row)
        signals.completed(None)


    def addProcessingOutput(self, *args):
        pass

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

        self.rimAgeValue = self.importedCellsByCol[Column.RIM_AGE].value
        self.rimAgeRawError = self.importedCellsByCol[Column.RIM_AGE_ERROR].value
        self.rimAgeStDev = utils.convert_to_stddev(
            self.rimAgeValue,
            self.rimAgeRawError,
            importSettings.rimAgeErrorType,
            importSettings.rimAgeErrorSigmas
        )
        rimAge = errors.ufloat(self.rimAgeValue, self.rimAgeStDev) * 10 ** 6

        self.mixedUPbValue = self.importedCellsByCol[Column.MIXED_U_PB].value
        self.mixedUPbRawError = self.importedCellsByCol[Column.MIXED_U_PB_ERROR].value
        self.mixedUPbStDev = utils.convert_to_stddev(
            self.mixedUPbValue,
            self.mixedUPbRawError,
            importSettings.mixedPointErrorType,
            importSettings.mixedPointErrorSigmas
        )
        mixedUPb = errors.ufloat(self.mixedUPbValue, self.mixedUPbStDev)

        self.mixedPbPbValue = self.importedCellsByCol[Column.MIXED_PB_PB].value
        self.mixedPbPbRawError = self.importedCellsByCol[Column.MIXED_PB_PB_ERROR].value
        self.mixedPbPbStDev = utils.convert_to_stddev(
            self.mixedPbPbValue,
            self.mixedPbPbRawError,
            importSettings.mixedPointErrorType,
            importSettings.mixedPointErrorSigmas
        )
        mixedPbPb = errors.ufloat(self.mixedPbPbValue, self.mixedPbPbStDev)

        rimUPb = calculations.u238pb206_from_age(rimAge)
        rimPbPb = calculations.pb207pb206_from_age(rimAge)

        self.rimUPbValue = errors.value(rimUPb)
        self.rimUPbStDev = errors.stddev(rimUPb)
        self.rimUPbError = utils.convert_from_stddev_with_sigmas(
            self.rimUPbValue,
            self.rimUPbStDev,
            calculationSettings.outputErrorType,
            calculationSettings.outputErrorSigmas
        )
        self.rimPbPbValue = errors.value(rimPbPb)
        self.rimPbPbStDev = errors.stddev(rimPbPb)
        self.rimPbPbError = utils.convert_from_stddev_with_sigmas(
            self.rimPbPbValue,
            self.rimPbPbStDev,
            calculationSettings.outputErrorType,
            calculationSettings.outputErrorSigmas
        )

        self.reconstructedAgeObj = calculations.discordant_age(rimUPb, rimPbPb, mixedUPb, mixedPbPb, calculationSettings.outputErrorSigmas)

        self.validOutput = self.reconstructedAgeObj is not None

        if not self.validOutput:
            self.calculatedCells = [CalculatedCell(None) for _ in range(9)]
            return

        self.reconstructedAge = self.reconstructedAgeObj.values[0] / (10 ** 6)
        self.reconstructedUPb = self.reconstructedAgeObj.values[1]
        self.reconstructedPbPb = self.reconstructedAgeObj.values[2]
        self.calculatedCells[0] = CalculatedCell(self.reconstructedAge)
        self.calculatedCells[3] = CalculatedCell(self.reconstructedUPb)
        self.calculatedCells[6] = CalculatedCell(self.reconstructedPbPb)

        if not self.reconstructedAgeObj.hasMinValue():
            self.validOutput = False
        else:
            self.minReconstructedAge = self.reconstructedAgeObj.minValues[0] / (10 ** 6)
            self.maxReconstructedUPb = self.reconstructedAgeObj.minValues[1]
            self.minReconstructedPbPb = self.reconstructedAgeObj.minValues[2]
            self.calculatedCells[1] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedAge, self.reconstructedAge - self.minReconstructedAge))
            self.calculatedCells[5] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedUPb, self.maxReconstructedUPb - self.reconstructedUPb))
            self.calculatedCells[7] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedPbPb, self.reconstructedPbPb - self.minReconstructedPbPb))

        if not self.reconstructedAgeObj.hasMaxValue():
            self.validOutput = False
        else:
            self.maxReconstructedAge = self.reconstructedAgeObj.maxValues[0] / (10 ** 6)
            self.minReconstructedUPb = self.reconstructedAgeObj.maxValues[1]
            self.maxReconstructedPbPb = self.reconstructedAgeObj.maxValues[2]
            self.calculatedCells[2] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedAge, self.maxReconstructedAge - self.reconstructedAge))
            self.calculatedCells[4] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedUPb, self.reconstructedUPb - self.minReconstructedUPb))
            self.calculatedCells[8] = CalculatedCell(calculationSettings.getOutputError(self.reconstructedPbPb, self.maxReconstructedPbPb - self.reconstructedPbPb))