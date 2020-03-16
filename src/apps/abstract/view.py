from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from utils.ui.statusBar import StatusBarWidget


class AbstractView(QWidget):

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.initUI()

    def initUI(self):
        self.graphPanel = self.createGraphWidget()
        self.dataPanel = self.createDataWidget()
        self.statusBar = StatusBarWidget()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.dataPanel)
        splitter.addWidget(self.graphPanel)
        splitter.setSizes([10000, 10000])
        splitter.setContentsMargins(1, 1, 1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter, 1)
        layout.addWidget(self.statusBar, 0)
        self.setLayout(layout)

    #######################
    ## Status signalling ##
    #######################

    def startTask(self, text):
        self.statusBar.startTask(text)

    def updateTask(self, value):
        self.statusBar.updateTask(value)

    def endTask(self, success, text):
        self.statusBar.endTask(success, text)

    ########
    ## IO ##
    ########

    def getInputFile(self):
        return QFileDialog.getOpenFileName(
            caption='Open CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests'
        )[0]
        #return '/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/data/unmixTest.csv'

    def getOutputFile(self):
        return QFileDialog.getSaveFileName(
            caption='Save CSV file',
            directory='/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/tests'
        )[0]

    def getSettings(self, settingsType, callback):
        settingsPopup = self.getSettingsDialog(settingsType)

        def outerCallback(result):
            if result == QDialog.Rejected:
                return None
            callback(settingsPopup.settings)

        settingsPopup.finished.connect(outerCallback)
        settingsPopup.show()

    ############
    ## Events ##
    ############

    def onCSVImportFinished(self, result, inputFile):
        if not result:
            self.endTask(False, "Failed to import CSV file")
            return

        self.dataPanel.afterSuccessfulCSVImport(inputFile)
        self.endTask(True, "Successfully imported CSV file")

    def onHeadersUpdated(self, headers):
        self.dataPanel.updateHeaders(headers)

    def onAllRowsUpdated(self, rows):
        self.dataPanel.updateAllRows(rows)

    def onRowUpdated(self, index, rowData):
        self.dataPanel.updateRow(index, rowData)

    def onProcessingStart(self):
        self.startTask("Processing data...")
        self.dataPanel.onProcessingStart()

    def onProcessingProgress(self, progress, *args):
        self.updateTask(progress)
        self.dataPanel.onProcessingProgress(*args)
        self.graphPanel.onProcessingProgress(*args)

    def onProcessingCompleted(self):
        self.endTask(True, "Successfully processed data")
        self.dataPanel.onProcessingEnd()

    def onProcessingCancelled(self):
        self.endTask(False, "Cancelled processing of data")
        self.dataPanel.onProcessingEnd()

    def onProcessingErrored(self, exception):
        self.endTask(False, "Error during processing of data")
        self.dataPanel.onProcessingEnd()
        QMessageBox.critical(None, "Error", "An error occurred during processing: \n\n" + exception.__class__.__name__ + ": " + str(exception))

    ##############
    ## Clean-up ##
    ##############

    def closeEvent(self, event):
        self.haltEvent.set()
