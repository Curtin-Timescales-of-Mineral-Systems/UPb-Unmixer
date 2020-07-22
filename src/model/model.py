from model.settings.type import SettingsType
from model.row import Row
from model.settings.calculation import UnmixCalculationSettings
from utils.settings import Settings


class UnmixModel:

    def __init__(self, signals):
        self.signals = signals
        self.rows = None

    def resetCalculations(self):
        importSettings = Settings.get(SettingsType.IMPORT)
        calculationSettings = Settings.get(SettingsType.CALCULATION)
        headers = importSettings.getHeaders() + calculationSettings.getHeaders()

        for row in self.rows:
            row.resetCalculatedCells()

        self.signals.headersUpdated.emit(headers)
        self.signals.allRowsUpdated.emit(self.rows)

    def updateRow(self, i, row):
        self.rows[i] = row
        self.signals.rowUpdated.emit(i, row, self.rows)

    def loadRawData(self, importSettings, rawHeaders, rawRows):
        self.rawHeaders = rawHeaders
        self.rows = [Row(row, importSettings) for row in rawRows]

        importHeaders = importSettings.getHeaders()
        calculationHeaders = UnmixCalculationSettings.getDefaultHeaders()
        headers = importHeaders + calculationHeaders

        self.signals.headersUpdated.emit(headers)
        self.signals.allRowsUpdated.emit(self.rows)

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

    def getNumberOfRejectedRows(self):
        return len([row for row in self.rows if row.rejected])

def process(signals, rows, calculationSettings):
    for i, row in enumerate(rows):
        if signals.halt():
            signals.cancelled()
            return
        row.process(calculationSettings)
        signals.progress((i + 1) / len(rows), i, row)
    signals.completed(None)
