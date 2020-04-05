from model.cell import ImportedCell, UncalculatedCell, CalculatedCell
from model.column import Column
from model.settings.calculation import UnmixCalculationSettings
from utils import calculations, errorUtils


class Row:
    def __init__(self, importedValues, importSettings):
        self.rawImportedValues = importedValues
        self.calculatedValues = None
        self.processed = False
        self.calculatedCellSpecs = UnmixCalculationSettings.getCalculatedColumnSpecs()

        displayedImportedColumns = importSettings.getDisplayColumnsWithRefs()
        self.importedCells = [ImportedCell(importedValues[i]) for _, i in displayedImportedColumns]
        self.importedCellsByCol = {col: self.importedCells[j] for j, (col, _) in enumerate(displayedImportedColumns)}
        self.validImports = all(cell.isValid() for cell in self.importedCells)
        self.resetCalculatedCells()

        self.processed = False
        self.validOutput = False

    def resetCalculatedCells(self):
        self.calculatedCells = [UncalculatedCell() for _ in self.calculatedCellSpecs]
        self.processed = False

    def getDisplayCells(self):
        return self.importedCells + self.calculatedCells

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

        self.reconstructedAgeObj = calculations.discordant_age(rimUPb, rimPbPb, mixedUPb, mixedPbPb,
                                                               calculationSettings.outputErrorSigmas)

        self.validOutput = self.reconstructedAgeObj is not None
        if not self.validOutput:
            self.calculatedCells = [CalculatedCell(None) for _ in range(9)]
            return
        self.validOutput = self.reconstructedAgeObj.fullyValid

        t, t_min, t_max = self.reconstructedAgeObj.getAge()
        u, u_min, u_max = self.reconstructedAgeObj.getUPb()
        p, p_min, p_max = self.reconstructedAgeObj.getPbPb()

        def getErrorCell(value, error):
            if error is None:
                return CalculatedCell(None)
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
