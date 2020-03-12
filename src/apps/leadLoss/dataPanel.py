from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QTableWidgetItem

from apps.abstract.dataPanel import AbstractDataPanel


class LeadLossDataPanel(AbstractDataPanel):

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self._initUI()

    #############
    ## UI spec ##
    #############

    def _initUI(self):
        self._initImportWidget()
        self._initDataTable()
        self._initActionButtonsWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.importWidget)
        layout.addWidget(self.dataTable)
        layout.addWidget(self.actionButtonsWidget)
        self.setLayout(layout)

        self.actionButtonsWidget.hide()


    def getActionButtons(self):
        return [self.importButton, self.processButton, self.exportButton]

    ############
    ## Events ##
    ############

    def onProcessingProgress(self, i, row):
        self.updateRow(i, row, True)

    def _refreshRowHeader(self, i, row, processed):
        header = QTableWidgetItem(str(i+1))

        if processed:
            colour = QColor(0, 255, 0, 27) if row.concordant else QColor(255, 0, 0, 27)
            header.setBackground(colour)
        self.dataTable.setVerticalHeaderItem(i, header)

    def _selectionChanged(self):
        pass