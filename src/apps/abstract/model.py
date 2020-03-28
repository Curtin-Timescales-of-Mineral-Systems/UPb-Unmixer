from utils import stringUtils


class ColumnSpec:
    def __init__(self, type):
        self.type = type

class Cell:
    def __init__(self, value, isImported):
        self.value = value
        self._isImported = isImported

    def isValid(self):
        return self.value is not None

    def isImported(self):
        return self._isImported

    def isCalculated(self):
        return not self._isImported


class ImportedCell(Cell):
    def __init__(self, rawValue):
        self._rawValue = rawValue
        try:
            value = float(rawValue)
        except:
            value = None
        super().__init__(value, True)

    def getDisplayString(self):
        if self.value is None:
            return self._rawValue
        return str(stringUtils.round_to_sf(self.value, 5))

class UncalculatedCell(Cell):
    def __init__(self):
        super().__init__(None, False)

    def isValid(self):
        True

    def getDisplayString(self):
        return ""

class CalculatedCell(Cell):
    def __init__(self, value):
        super().__init__(value, False)

    def isValid(self):
        return self.value is not None

    def getDisplayString(self):
        if self.value is None:
            return ""
        return str(stringUtils.round_to_sf(self.value, 5))


class AbstractModel:

    def __init__(self):
        pass

    def updateRow(self, i, row):
        self.rows[i] = row

    def resetCalculations(self):
        for row in self.rows:
            row.resetCalculatedCells()


class AbstractRow:

    def __init__(self, importedValues, importSettings, calculatedCellSpecs):
        self.rawImportedValues = importedValues
        self.calculatedValues = None
        self.processed = False
        self.calculatedCellSpecs = calculatedCellSpecs

        displayedImportedColumns = importSettings.getDisplayColumnsWithRefs()
        self.importedCells = [ImportedCell(importedValues[i]) for _, i in displayedImportedColumns]
        self.importedCellsByCol = {col:self.importedCells[j] for j, (col, _) in enumerate(displayedImportedColumns)}
        self.validImports = all(cell.isValid() for cell in self.importedCells)
        self.resetCalculatedCells()

    def setCalculatedValues(self, calculatedValues):
        self.calculatedValues = calculatedValues

    def getExportedValues(self, exportSettings):
        return

    def getDisplayCells(self):
        return self.importedCells + self.calculatedCells

    def resetCalculatedCells(self):
        self.calculatedCells = [UncalculatedCell() for _ in self.calculatedCellSpecs]
        self.processed = False