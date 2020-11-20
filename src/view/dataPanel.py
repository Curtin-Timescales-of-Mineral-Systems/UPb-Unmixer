from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLineEdit, QStyle, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem

from model.cell import Cell
from model.model import Model
from model.signals import Signals
from model.spot import Spot
from utils import config
from utils.string import pluralise
from utils.ui import uiUtils


class DataPanel(QGroupBox):

    def __init__(self, application):
        super().__init__("Data")

        self._application = application
        self._init_ui()
        self._init_signals(application.signals)

    ###############
    # UI creation #
    ###############

    def _init_signals(self, signals: Signals):
        signals.csv_imported.connect(self._on_csv_imported)

        signals.headers_updated.connect(self._on_headers_updated)
        signals.row_updated.connect(self._on_row_updated)
        signals.all_rows_updated.connect(self._on_all_rows_updated)

        signals.processing_started.connect(self._on_processing_start)
        signals.processing_completed.connect(self._on_processing_end)
        signals.processing_errored.connect(self._on_processing_end)
        signals.processing_cancelled.connect(self._on_processing_end)

    def _init_ui(self):
        self._init_import_widget()
        self._init_warning_labels()
        self._init_data_table()
        self._init_action_buttons_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.importWidget)
        layout.addWidget(self.data_table)
        layout.addWidget(self.warningsWidget)
        layout.addWidget(self.actionButtonsWidget)
        self.setLayout(layout)

        self.actionButtonsWidget.hide()

    def _init_import_widget(self):
        self.importButton = QPushButton("  Import CSV")
        self.importButton.clicked.connect(self._application.import_csv)
        self.importButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        self.importFileText = QLineEdit("")
        self.importFileText.setReadOnly(True)

        self.helpButton = QPushButton("  Help")
        self.helpButton.clicked.connect(self._application.show_help)
        self.helpButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))

        layout = QHBoxLayout()
        layout.addWidget(self.importButton)
        layout.addWidget(self.importFileText)
        layout.addWidget(self.helpButton)
        layout.setContentsMargins(0, 0, 0, 5)

        self.importWidget = QWidget()
        self.importWidget.setLayout(layout)

    def _init_warning_labels(self):
        self.invalidDataWidget, self.invalidDataLabel = uiUtils.createIconWithLabel(
            self.style().standardIcon(QStyle.SP_MessageBoxCritical), "Hi")
        self.invalidCalculationWidget, self.invalidCalculationLabel = uiUtils.createIconWithLabel(
            self.style().standardIcon(QStyle.SP_MessageBoxWarning), "Hi2")
        self.rejectedCalculationWidget, self.rejectedCalculationLabel = uiUtils.createIconWithLabel(
            self.style().standardIcon(QStyle.SP_MessageBoxWarning), "hi")
        self.validCalculationWidget, self.validCalculationLabel = uiUtils.createIconWithLabel(
            self.style().standardIcon(QStyle.SP_DialogApplyButton), "hi")

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

    def _init_data_table(self):
        self.data_table = QTableWidget(1, 1)
        self.data_table.resizeColumnsToContents()
        self.data_table.resizeRowsToContents()
        self.data_table.hide()
        self.data_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        uiUtils.retainSizeWhenHidden(self.data_table)

    def _init_table_widget_item(self, content):
        cell = QTableWidgetItem(str(content))
        cell.setTextAlignment(Qt.AlignHCenter)
        cell.setFlags(cell.flags() ^ Qt.ItemIsEditable)
        return cell

    def _init_action_buttons_widget(self):
        self.processButton = QPushButton("  Process")
        self.processButton.clicked.connect(self._application.process)
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))

        self.exportButton = QPushButton("  Export CSV")
        self.exportButton.clicked.connect(self._application.exportCSV)
        self.exportButton.setEnabled(False)
        self.exportButton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        self.actionButtonsWidget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.processButton)
        layout.addWidget(self.exportButton)
        self.actionButtonsWidget.setLayout(layout)

    ####################
    # Event processing #
    ####################

    def _on_csv_imported(self, success: bool, input_file: str) -> None:
        if not success:
            return

        self.importFileText.setText(input_file)

        self.data_table.show()
        self.actionButtonsWidget.show()
        self.exportButton.show()

    def _on_table_selection_changed(self) -> None:
        row_indices = sorted(set(index.row() for index in self.data_table.selectedIndexes()))
        self._application.selectRows(row_indices)

    def _on_processing_start(self) -> None:
        for button in self.getActionButtons():
            button.setEnabled(button == self.processButton)
        self.processButton.setEnabled(True)
        self.processButton.setText("  Cancel processing")
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.processButton.clicked.disconnect(self._application.process)
        self.processButton.clicked.connect(self._application.cancelProcessing)

    def _on_processing_end(self) -> None:
        for button in self.getActionButtons():
            button.setEnabled(True)
        self.processButton.setText("  Process")
        self.processButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.processButton.clicked.disconnect(self._application.cancelProcessing)
        self.processButton.clicked.connect(self._application.process)

    def _on_headers_updated(self) -> None:
        headers = self._application.model.get_headers_for_display()
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)

    def _on_all_rows_updated(self) -> None:
        rows = self._application.model.get_spots()
        self.data_table.setRowCount(len(rows))
        for i in range(len(rows)):
            self._on_row_updated(i)

    def _on_row_updated(self, i: int) -> None:
        rows = self._application.model.get_spots()
        row = rows[i]

        self._refresh_row_header(i, row)
        self._refresh_row_data(i, row)
        self._refresh_warning_labels(rows)

        self.data_table.resizeColumnsToContents()
        self.data_table.resizeRowsToContents()

    ###########
    # Actions #
    ###########

    def _refresh_warning_labels(self, spots: List[Spot]) -> None:
        rows_with_invalid_inputs = len([spot for spot in spots if spot.has_invalid_inputs()])
        rows_with_invalid_outputs = len([spot for spot in spots if spot.has_invalid_outputs()])
        rows_with_rejected_outputs = len([spot for spot in spots if spot.has_rejected_outputs()])
        rows_accepted = len([spot for spot in spots if spot.has_accepted_outputs()])

        self.invalidDataWidget.setVisible(rows_with_invalid_inputs > 0)
        self.invalidCalculationWidget.setVisible(rows_with_invalid_outputs > 0)
        self.rejectedCalculationWidget.setVisible(rows_with_rejected_outputs > 0)
        self.validCalculationWidget.setVisible(rows_accepted > 0)

        self.invalidDataLabel.setText(f'{pluralise("spot", rows_with_invalid_inputs)} with invalid data imported from the CSV file.')
        self.invalidCalculationLabel.setText(f'{pluralise("spot", rows_with_invalid_outputs)} for which reconstructed core age cannot be calculated.')
        self.rejectedCalculationLabel.setText(f'{pluralise("spot", rows_with_rejected_outputs)} for which the calculated reconstructed core age is deemed unreliable.')
        self.validCalculationLabel.setText(f'{pluralise("spot", rows_accepted)} for which the core age was successfully reconstructed.')

    def _refresh_row_header(self, i: int, spot: Spot) -> None:
        header = self._init_table_widget_item(i + 1)
        self.data_table.setVerticalHeaderItem(i, header)

        if spot.has_invalid_inputs():
            header.setBackground(config.Q_INVALID_IMPORT_COLOUR)
            return

        if not spot.has_outputs():
            return
        if spot.has_invalid_outputs():
            header.setBackground(config.Q_INVALID_CALCULATION_COLOUR)
            return
        if spot.has_rejected_outputs():
            header.setBackground(config.Q_REJECTED_CALCULATION_COLOUR)
            return
        header.setBackground(config.Q_VALID_CALCULATION_COLOUR)

    def _refresh_row_data(self, i: int, spot: Spot) -> None:
        for j, cell in enumerate(spot.get_display_cells()):
            table_cell = self._init_table_widget_item(cell.get_display_string())
            self._set_cell_colour(table_cell, spot, cell, j)
            self.data_table.setItem(i, j, table_cell)
        self.data_table.viewport().update()
        self.data_table.resizeColumnsToContents()

    def _set_cell_colour(self, table_cell, spot: Spot, data_cell: Cell, cell_number: int) -> None:
        if data_cell.is_valid():
            if spot.has_rejected_outputs() and cell_number == 20:
                table_cell.setBackground(config.Q_REJECTED_CALCULATION_COLOUR)
            return

        if spot.has_invalid_inputs():
            colour = config.Q_INVALID_IMPORT_COLOUR
        else:
            colour = config.Q_INVALID_CALCULATION_COLOUR
        table_cell.setBackground(colour)

    #############
    # Utilities #
    #############

    def getActionButtons(self):
        return [self.importButton, self.processButton, self.exportButton]
