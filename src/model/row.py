from model.cell import ImportedCell, UncalculatedCell, CalculatedCell
from model.column import Column
from model.settings.calculation import UnmixCalculationSettings
from utils import calculations, errorUtils

class Row:
    def __init__(self, importedValues, importSettings):
        self.rawImportedValues = importedValues
        self.calculatedValues = None
        self.calculatedCells = None
        self.processed = False
        self.rejected = False

        displayedImportedColumns = importSettings.getDisplayColumnsWithRefs()
        self.importedCells = [ImportedCell(importedValues[i]) for _, i in displayedImportedColumns]
        self.validImports = all(cell.isValid() for cell in self.importedCells)
        self.resetCalculatedCells()

        self.processed = False
        self.validOutput = False

        if not self.validImports:
            return

        values = {col: self.importedCells[j].value for j, (col, _) in enumerate(displayedImportedColumns)}

        self.rimAgeValue = values[Column.RIM_AGE_VALUE]
        rimAgeRawError = values[Column.RIM_AGE_ERROR]
        self.rimAgeStDev = calculations.convert_to_stddev(self.rimAgeValue, rimAgeRawError, importSettings.rimAgeErrorType, importSettings.rimAgeErrorSigmas)

        self.mixedUPbValue = values[Column.MIXED_U_PB_VALUE]
        mixedUPbRawError = values[Column.MIXED_U_PB_ERROR]
        self.mixedUPbStDev = calculations.convert_to_stddev(self.mixedUPbValue, mixedUPbRawError, importSettings.mixedUPbErrorType, importSettings.mixedUPbErrorSigmas)

        self.mixedPbPbValue = values[Column.MIXED_PB_PB_VALUE]
        mixedPbPbRawError = values[Column.MIXED_PB_PB_ERROR]
        self.mixedPbPbStDev = calculations.convert_to_stddev(self.mixedPbPbValue, mixedPbPbRawError, importSettings.mixedPbPbErrorType, importSettings.mixedPbPbErrorSigmas)

        self.uConcentration = values[Column.U_CONCENTRATION]
        self.thConcentration = values[Column.TH_CONCENTRATION]

    def resetCalculatedCells(self):
        self.calculatedCells = [UncalculatedCell() for _ in UnmixCalculationSettings.getCalculatedColumnHeaders()]
        self.processed = False
        self.rejected = False

    def getDisplayCells(self):
        return self.importedCells + self.calculatedCells

    def process(self, settings):
        self.processed = True

        if not self.validImports:
            self.calculatedCells = [CalculatedCell(None) for _ in range(13)]
            return

        rimAge = errorUtils.ufloat(self.rimAgeValue, self.rimAgeStDev) * 10 ** 6
        mixedUPb = errorUtils.ufloat(self.mixedUPbValue, self.mixedUPbStDev)
        mixedPbPb = errorUtils.ufloat(self.mixedPbPbValue, self.mixedPbPbStDev)

        rimUPb = calculations.u238pb206_from_age(rimAge)
        rimPbPb = calculations.pb207pb206_from_age(rimAge)

        self.rimUPbValue = errorUtils.value(rimUPb)
        self.rimUPbStDev = errorUtils.stddev(rimUPb)
        self.rimUPbError = calculations.convert_from_stddev_with_sigmas(self.rimUPbValue, self.rimUPbStDev, settings.outputErrorType, settings.outputErrorSigmas)

        self.rimPbPbValue = errorUtils.value(rimPbPb)
        self.rimPbPbStDev = errorUtils.stddev(rimPbPb)
        self.rimPbPbError = calculations.convert_from_stddev_with_sigmas(self.rimPbPbValue, self.rimPbPbStDev, settings.outputErrorType, settings.outputErrorSigmas)

        self.reconstructedAgeObj = calculations.discordant_age(rimUPb, rimPbPb, mixedUPb, mixedPbPb, settings.outputErrorSigmas)

        self.validOutput = self.reconstructedAgeObj is not None
        if not self.validOutput:
            self.calculatedCells = [CalculatedCell(None) for _ in range(13)]
            return
        self.validOutput = self.reconstructedAgeObj.fullyValid

        t, t_min, t_max = self.reconstructedAgeObj.getAge()
        u, u_min, u_max = self.reconstructedAgeObj.getUPb()
        p, p_min, p_max = self.reconstructedAgeObj.getPbPb()

        metamictScore = calculations.metamictScore(calculations.alphaDamage(self.uConcentration, self.thConcentration, t)) if t else 0
        rimAgePrecisionScore = calculations.rimAgePrecisionScore(self.rimAgeValue, self.rimAgeStDev*2)
        coreToRimScore = calculations.coreToRimScore(self.rimUPbValue, self.rimPbPbValue, self.mixedUPbValue, self.mixedPbPbValue, u, p) if u and p else 0
        totalScore = metamictScore * rimAgePrecisionScore * coreToRimScore
        self.rejected = totalScore < 0.5

        def getErrorCell(value, error):
            if error is None:
                return CalculatedCell(None)
            else:
                return CalculatedCell(settings.getOutputError(value, error))

        self.calculatedCells[0] = CalculatedCell(t)
        self.calculatedCells[1] = getErrorCell(t, t_min)
        self.calculatedCells[2] = getErrorCell(t, t_max)

        self.calculatedCells[3] = CalculatedCell(u)
        self.calculatedCells[4] = getErrorCell(u, u_min)
        self.calculatedCells[5] = getErrorCell(u, u_max)

        self.calculatedCells[6] = CalculatedCell(p)
        self.calculatedCells[7] = getErrorCell(p, p_min)
        self.calculatedCells[8] = getErrorCell(p, p_max)

        self.calculatedCells[9] = CalculatedCell(metamictScore)
        self.calculatedCells[10] = CalculatedCell(rimAgePrecisionScore)
        self.calculatedCells[11] = CalculatedCell(coreToRimScore)
        self.calculatedCells[12] = CalculatedCell(totalScore)
