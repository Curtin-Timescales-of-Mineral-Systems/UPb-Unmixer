from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import utils


class AbstractDataPanel(QGroupBox):

    def __init__(self, controller, *args, **kwargs):
        super(AbstractDataPanel, self).__init__("Data", *args, **kwargs)

        self.controller = controller

    #############
    ## UI spec ##
    #############

    def _initImportWidget(self):
        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self.controller.importCSV)
        self.importFileText = QLineEdit("")
        self.importFileText.setReadOnly(True)

        self.importWidget = QWidget()
        importWidgetLayout = QHBoxLayout()
        importWidgetLayout.addWidget(self.importButton)
        importWidgetLayout.addWidget(self.importFileText)
        importWidgetLayout.setContentsMargins(0,0,0,5)
        self.importWidget.setLayout(importWidgetLayout)

    def _initDataTable(self):
        self.dataTable = QTableWidget(1, 1)
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()
        self.dataTable.hide()
        self.dataTable.itemSelectionChanged.connect(self._selectionChanged)
        utils.retainSize(self.dataTable)

    def _initTableWidgetItem(self, content):
        cell = QTableWidgetItem(str(content))
        cell.setTextAlignment(Qt.AlignHCenter)
        cell.setFlags(cell.flags() ^ Qt.ItemIsEditable)
        return cell

    def _initActionButtonsWidget(self):
        self.processButton = QPushButton("Process")
        self.processButton.clicked.connect(self.controller.process)

        self.exportButton = QPushButton("Export CSV")
        self.exportButton.clicked.connect(self.controller.exportCSV)
        self.exportButton.setEnabled(False)

        self.actionButtonsWidget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.processButton)
        layout.addWidget(self.exportButton)
        self.actionButtonsWidget.setLayout(layout)

    #############
    ## Updates ##
    #############

    def afterSuccessfulCSVImport(self, inputFile):
        self.importFileText.setText(inputFile)

        self.dataTable.show()
        self.actionButtonsWidget.show()

    def onProcessingStart(self):
        for button in self.getActionButtons():
            button.setEnabled(button == self.processButton)
        self.processButton.setEnabled(True)
        self.processButton.setText("Cancel processing")
        self.processButton.clicked.disconnect(self.controller.process)
        self.processButton.clicked.connect(self.controller.cancelProcessing)

    def onProcessingEnd(self):
        for button in self.getActionButtons():
            button.setEnabled(True)
        self.processButton.setText("Process")
        self.processButton.clicked.disconnect(self.controller.cancelProcessing)
        self.processButton.clicked.connect(self.controller.process)

    def updateHeaders(self, headers):
        self.dataTable.setColumnCount(len(headers))
        self.dataTable.setHorizontalHeaderLabels(headers)

    def updateAllRows(self, rows):
        self.dataTable.setRowCount(len(rows))
        for index, row in enumerate(rows):
            self.updateRow(index, row, False)

    def updateRow(self, i, row, processed):
        self._refreshRowHeader(i, row, processed)
        self._refreshRowData(i, row)

        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()

    def _refreshRowData(self, i, row):
        for j, cell in enumerate(row.getDisplayCells()):
            tableCell = self._initTableWidgetItem(cell.getDisplayString())
            if not cell.isValid():
                if cell.isImported():
                    tableCell.setBackground(QColor(255, 0, 0, 27))
                elif row.validImports and row.processed:
                    tableCell.setBackground(QColor(255, 165, 0, 27))
            self.dataTable.setItem(i, j, tableCell)
        self.dataTable.viewport().update()
        self.dataTable.resizeColumnsToContents()
