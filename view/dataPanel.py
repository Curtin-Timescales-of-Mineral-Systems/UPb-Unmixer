import time
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import csv_mode
import utils

from view.settingsDialog import SettingsDialog

class DataPanel(QGroupBox):

    _progressSignal = pyqtSignal(int)

    ########
    ## UI ##
    ########

    def __init__(self, app, *args, **kwargs):
        super(DataPanel, self).__init__("Data", *args, **kwargs)
        self.app = app
        self.initUI()

        self.mainButtons = [self.importButton, self.processButton, self.exportButton]

        self.threadpool = QThreadPool()
        self.haltEvent = threading.Event()
        self.haltEvent.set()

    def initUI(self):
        importWidget = self.initImportWidget()
        exportWidget = self.initExportWidget()

        self.dataTable = QTableWidget(1, self.app.settings.getNumberOfDisplayColumns())
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()
        self.dataTable.hide()
        self.dataTable.itemSelectionChanged.connect(self._selectionChanged)

        utils.retainSize(self.dataTable)

        layout = QVBoxLayout()
        layout.addWidget(importWidget)
        layout.addWidget(self.dataTable)
        layout.addWidget(exportWidget)
        self.setLayout(layout)

    def initImportWidget(self):
        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self._startCSVImport)
        self.importFileText = QLineEdit("")
        self.importFileText.setReadOnly(True)

        importWidget = QWidget()
        importWidgetLayout = QHBoxLayout()
        importWidgetLayout.addWidget(self.importButton)
        importWidgetLayout.addWidget(self.importFileText)
        importWidgetLayout.setContentsMargins(0,0,0,5)
        importWidget.setLayout(importWidgetLayout)
        return importWidget

    def initExportWidget(self):
        self.processButton = QPushButton("Process")
        self.processButton.clicked.connect(self._startProcessing)
        self.processButton.hide()

        self.exportButton = QPushButton("Export CSV")
        self.exportButton.clicked.connect(self.exportCSV)
        self.exportButton.hide()

        exportWidget = QWidget()
        exportWidgetLayout = QHBoxLayout()
        exportWidgetLayout.addWidget(self.processButton)
        exportWidgetLayout.addWidget(self.exportButton)
        exportWidget.setLayout(exportWidgetLayout)
        return exportWidget

    ######################
    ## Event processing ##
    ######################

    def _selectionChanged(self):
        rowIndices = sorted(set(index.row() for index in self.dataTable.selectedIndexes()))
        row = self.rows[rowIndices[0]]
        self.app.graphPanel.displayRow(row, self.app.settings)


    def _startCSVImport(self):
        self.inputFile = QFileDialog.getOpenFileName(self, 'Open file', '/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/data')[0]
        if not self.inputFile:
            return

        self.settingsPopup = SettingsDialog(self.app.settings)
        self.settingsPopup.setModal(True)
        self.settingsPopup.finished.connect(self._continueCSVImport)
        result = self.settingsPopup.show()

    def _continueCSVImport(self, result):
        if result == QDialog.Rejected:
            return

        self.app.settings = self.settingsPopup.settings
        self.app.settings.save()
        self.app.statusBar.startTask("Importing CSV file...", False)

        #self._endCSVImport(self._csvImport())
        self.runAsyncTask(self._csvImport, self._endCSVImport, self.importButton, "Cancel import")

    def _csvImport(self):
        self.rawHeaders, self.rows = csv_mode.read_input(self.inputFile, self.app.settings)
        return True

    def _endCSVImport(self, complete, result):
        if not complete:
            self.app.statusBarWidget.endTask(False, "Cancelled import of CSV file")
            return

        if not result:
            self.app.statusBarWidget.endTask(False, "Failed to import CSV file")
            error_dialog = QMessageBox.critical(None, "Error", str(error))
            return

        self.importFileText.setText(self.inputFile)

        displayHeaders = self.app.settings.getAllDisplayHeaders()
        self.dataTable.setHorizontalHeaderLabels(displayHeaders)
        self.dataTable.setRowCount(len(self.rows)-1)
        for i in range(len(self.rows)):
            self._refreshTableRow(i, False)

        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()

        self.dataTable.show()
        self.exportButton.show()
        self.processButton.show()

        self.app.statusBar.endTask(True, "Successfully imported CSV file")

    def exportCSV(self):
        outputFile = QFileDialog.getSaveFileName(self, 'Open file', '/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/data')[0]
        if not outputFile:
            return

        headers = self.rawHeaders + self.app.settings.getOutputDataHeaders()

        self.app.statusBar.startTask("Exporting CSV file", False)

        try:
            csv_mode.write_output(headers, self.rows, outputFile)
            self.app.statusBar.endTask(True, "Successfully exported CSV file")
        except Exception as e:
            self.app.statusBar.endTask(False, "Failed to export CSV file")

    def _startProcessing(self):
        if not self.haltEvent.is_set():
            self.processButton.setText(self.processButton.originalText)
            self.haltEvent.set()
            return

        self.app.statusBar.startTask("Processing CSV file...", len(self.rows), self._progressSignal)
        self.runAsyncTask(self._process, self._endProcessing, self.processButton, "Cancel processing")
        self._progressSignal.connect(self._onRowProcessed)

    def _process(self):
        for i, row in enumerate(self.rows):
            if self.haltEvent.is_set():
                return
            row.process(self.app.settings)
            self._progressSignal.emit(i)

    def _endProcessing(self, complete, result):
        self._progressSignal.disconnect(self._onRowProcessed)

        if not complete:
            self.app.statusBar.endTask(False, "Cancelled processing of data")
            return

        self.app.statusBar.endTask(True, "Successfully processed data")

    ###############
    ## Utilities ##
    ###############

    def _onRowProcessed(self, i):
        self._refreshTableRow(i, True)

    def runAsyncTask(self, function, callback, button, updatedText):
        button.originalText = button.text()
        button.setText(updatedText)
        for b in self.mainButtons:
            b.setEnabled(b == button)

        worker = _Worker(function)

        def outerCallback():
            callback(not self.haltEvent.is_set(), worker.result)
            for b in self.mainButtons:
                b.setEnabled(True)
            button.setText(button.originalText)
            self.haltEvent.set()

        self.haltEvent.clear()
        worker.signals.finished.connect(outerCallback)
        self.threadpool.start(worker)

    def _colourTableRowHeader(self, i, processing=True):
        row = self.rows[i]

    def _refreshTableRow(self, i, processing):
        self._refreshRowHeader(i, processing)
        self._refreshRowData(i)

    def _refreshRowHeader(self, i, processing):
        row = self.rows[i]
        header = QTableWidgetItem(str(i+1))
        self.dataTable.setVerticalHeaderItem(i, header)
        if not row.validInput: 
            header.setBackground(QColor(255, 0, 0, 27))
            return
        if not row.processed:
            return
        if not row.validOutput: 
            header.setBackground(QColor(255, 165, 0, 27))
            return
        header.setBackground(QColor(0, 255, 0, 27))

    def _refreshRowData(self, i):
        row = self.rows[i]
        displayValues = row.getDisplayValues(self.app.settings)
        for j, item in enumerate(displayValues):
            displayValue = utils.round_to_sf(item, 5) if isinstance(item, float) else item
            cell = QTableWidgetItem(str(displayValue))
            cell.setTextAlignment(Qt.AlignHCenter)
            cell.setFlags(cell.flags() ^ Qt.ItemIsEditable)
            if j < 6 and not row.cellValid[j]:
                cell.setBackground(QColor(255, 0, 0, 27))
            elif row.validInput and row.processed and not item and j >= 6:
                cell.setBackground(QColor(255, 165, 0, 27))
            self.dataTable.setItem(i, j, cell)
        self.dataTable.viewport().update()
        self.dataTable.resizeColumnsToContents()


    def closeEvent(self, event):
        self.haltEvent.set()

class _Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(_Worker, self).__init__()
        self.fn = fn
        self.signals = _WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.result = self.fn()
            self.signals.finished.emit()
        except Exception as e:
            self.signals.finished.emit()
            raise e

class _WorkerSignals(QObject):
    finished = pyqtSignal()