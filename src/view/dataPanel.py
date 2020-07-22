from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLineEdit, QStyle, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem, QLabel

from utils.stringUtils import pluralise
from utils.ui import uiUtils


class UnmixDataPanel(QGroupBox):

    INVALID_IMPORT_ROW_COLOUR = QColor(255, 0, 0, 27)
    INVALID_CALCULATION_ROW_COLOUR = QColor(255, 165, 0, 27)
    REJECTED_CALCULATION_ROW_COLOUR = QColor(255, 255, 0, 27)
    VALID_ROW_COLOUR = QColor(0, 255, 0, 27)

    def __init__(self, controller, *args, **kwargs):
        super().__init__("Data", *args, **kwargs)

        self.controller = controller

        self.controller.signals.headersUpdated.connect(self.onHeadersUpdated)
        self.controller.signals.rowUpdated.connect(self.onRowUpdated)
        self.controller.signals.allRowsUpdated.connect(self.onAllRowsUpdated)

        self.controller.signals.processingStarted.connect(self.onProcessingStart)
        self.controller.signals.processingCompleted.connect(self.onProcessingEnd)
        self.controller.signals.processingErrored.connect(self.onProcessingEnd)
        self.controller.signals.processingCancelled.connect(self.onProcessingEnd)

        self._initUI()

    #############
    ## UI spec ##
    #############

    def _initUI(self):
        self._initImportWidget()
        self._initWarningLabels()
        self._initDataTable()
        self._initActionButtonsWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.importWidget)
        layout.addWidget(self.dataTable)
        layout.addWidget(self.warningsWidget)
        layout.addWidget(self.actionButtonsWidget)
        self.setLayout(layout)

        self.actionButtonsWidget.hide()

    def _initImportWidget(self):

        self.importButton = QPushButton("  Import CSV")
        self.importButton.clicked.connect(self.controller.importCSV)
        self.importButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        self.importFileText = QLineEdit("")
        self.importFileText.setReadOnly(True)

        self.helpButton = QPushButton("  Help")
        self.helpButton.clicked.connect(self.controller.showHelp)
        self.helpButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))

        layout = QHBoxLayout()
        layout.addWidget(self.importButton)
        layout.addWidget(self.importFileText)
        layout.addWidget(self.helpButton)
        layout.setContentsMargins(0, 0, 0, 5)

        self.importWidget = QWidget()
        self.importWidget.setLayout(layout)

    def _initWarningLabels(self):
        self.invalidDataWidget, self.invalidDataLabel = uiUtils.createIconWithLabel(self.style().standardIcon(QStyle.SP_MessageBoxCritical), "Hi")
        self.invalidCalculationWidget, self.invalidCalculationLabel = uiUtils.createIconWithLabel(self.style().standardIcon(QStyle.SP_MessageBoxWarning), "Hi2")
        self.rejectedCalculationWidget, self.rejectedCalculationLabel = uiUtils.createIconWithLabel(self.style().standardIcon(QStyle.SP_MessageBoxWarning), "hi")
        self.validCalculationWidget, self.validCalculationLabel = uiUtils.createIconWithLabel(self.style().standardIcon(QStyle.SP_DialogApplyButton), "hi")

        self.invalidDataWidget.setVisible(False)
        self.invalidCalculationWidget.setVisible(False)
        self.rejectedCalculationWidget.setVisible(False)
        self.validCalculationWidget.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.invalidDataWidget)
        layout.addWidget(self.invalidCalculationWidget)
        layout.addWidget(self.rejectedCalculationWidget)
        layout.addWidget(self.validCalculationWidget)
        layout.setContentsMargins(0, 0, 0, 5)

        self.warningsWidget = QWidget()
        self.warningsWidget.setLayout(layout)

    def _initDataTable(self):
        self.dataTable = QTableWidget(1, 1)
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()
        self.dataTable.hide()
        self.dataTable.itemSelectionChanged.connect(self._selectionChanged)
        uiUtils.retainSizeWhenHidden(self.dataTable)

    def _initTableWidgetItem(self, content):
        cell = QTableWidgetItem(str(content))
        cell.setTextAlignment(Qt.AlignHCenter)
        cell.setFlags(cell.flags() ^ Qt.ItemIsEditable)
        return cell

    def _initActionButtonsWidget(self):
        self.processButton = QPushButton("  Process")
        self.processButton.clicked.connect(self.controller.process)
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))

        self.exportButton = QPushButton("  Export CSV")
        self.exportButton.clicked.connect(self.controller.exportCSV)
        self.exportButton.setEnabled(False)
        self.exportButton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        self.actionButtonsWidget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.processButton)
        layout.addWidget(self.exportButton)
        self.actionButtonsWidget.setLayout(layout)

    ######################
    ## Event processing ##
    ######################

    def afterSuccessfulCSVImport(self, inputFile):
        self.importFileText.setText(inputFile)

        self.dataTable.show()
        self.actionButtonsWidget.show()
        self.exportButton.show()

    def _selectionChanged(self):
        rowIndices = sorted(set(index.row() for index in self.dataTable.selectedIndexes()))
        self.controller.selectRows(rowIndices)

    def onProcessingStart(self):
        for button in self.getActionButtons():
            button.setEnabled(button == self.processButton)
        self.processButton.setEnabled(True)
        self.processButton.setText("  Cancel processing")
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.processButton.clicked.disconnect(self.controller.process)
        self.processButton.clicked.connect(self.controller.cancelProcessing)

    def onProcessingEnd(self):
        for button in self.getActionButtons():
            button.setEnabled(True)
        self.processButton.setText("  Process")
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.processButton.clicked.disconnect(self.controller.cancelProcessing)
        self.processButton.clicked.connect(self.controller.process)

    def onHeadersUpdated(self, headers):
        self.dataTable.setColumnCount(len(headers))
        self.dataTable.setHorizontalHeaderLabels(headers)

    def onAllRowsUpdated(self, rows):
        self.dataTable.setRowCount(len(rows))
        for index, row in enumerate(rows):
            self.onRowUpdated(index, row, rows)

    def onRowUpdated(self, i, row, allRows):
        self._refreshRowHeader(i, row)
        self._refreshRowData(i, row)
        self._refreshWarningLabels(allRows)

        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()


    def _refreshWarningLabels(self, rows):
        invalidDataRows = len([row for row in rows if not row.validImports])
        invalidCalculationRows = len([row for row in rows if row.validImports and row.processed and not row.validOutput])
        rejectedCalculationRows = len([row for row in rows if row.validImports and row.processed and row.rejected])
        acceptedRows =  len([row for row in rows if row.processed and row.validOutput and not row.rejected])

        self.invalidDataWidget.setVisible(invalidDataRows > 0)
        self.invalidCalculationWidget.setVisible(invalidCalculationRows > 0)
        self.rejectedCalculationWidget.setVisible(rejectedCalculationRows > 0)
        self.validCalculationWidget.setVisible(acceptedRows > 0)

        self.invalidDataLabel.setText(pluralise("spot", invalidDataRows) + " with invalid data imported from the CSV file.")
        self.invalidCalculationLabel.setText(pluralise("spot", invalidCalculationRows) + " for which reconstructed core age cannot be calculated.")
        self.rejectedCalculationLabel.setText(pluralise("spot", rejectedCalculationRows) + " for which the calculated reconstructed core age is deemed unreliable.")
        self.validCalculationLabel.setText(pluralise("spot", acceptedRows) + " for which the core age was successfully reconstructed.")

    def _refreshRowHeader(self, i, row):
        header = self._initTableWidgetItem(i + 1)
        self.dataTable.setVerticalHeaderItem(i, header)

        if not row.validImports:
            header.setBackground(self.INVALID_IMPORT_ROW_COLOUR)
            return
        if not row.processed:
            return
        if not row.validOutput:
            header.setBackground(self.INVALID_CALCULATION_ROW_COLOUR)
            return
        if row.rejected:
            header.setBackground(self.REJECTED_CALCULATION_ROW_COLOUR)
            return
        header.setBackground(self.VALID_ROW_COLOUR)

    def _refreshRowData(self, i, row):
        print("")
        for j, cell in enumerate(row.getDisplayCells()):
            tableCell = self._initTableWidgetItem(cell.getDisplayString())
            self._setCellColour(tableCell, row, cell, j)
            self.dataTable.setItem(i, j, tableCell)
        self.dataTable.viewport().update()
        self.dataTable.resizeColumnsToContents()

    def _setCellColour(self, tableCell, row, dataCell, cellNumber):
        if dataCell.isValid():
            if row.rejected and cellNumber == 20:
                tableCell.setBackground(self.REJECTED_CALCULATION_ROW_COLOUR)
            return

        if not row.validImports:
            colour = self.INVALID_IMPORT_ROW_COLOUR
        else:
            colour = self.INVALID_CALCULATION_ROW_COLOUR
        tableCell.setBackground(colour)

    ###############
    ## Utilities ##
    ###############

    def getActionButtons(self):
        return [self.importButton, self.processButton, self.exportButton]
