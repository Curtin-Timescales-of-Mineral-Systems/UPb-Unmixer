from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from tabs.unmix.controller import UnmixTabController
from tabs.leadLoss.controller import LeadLossTabController

from tabs.leadLoss.settings.exports import LeadLossExportSettings
from tabs.leadLoss.settings.imports import LeadLossImportSettings
from tabs.leadLoss.settings.calculation import LeadLossCalculationSettings
from tabs.unmix.settings.imports import UnmixImportSettings

import sys

class Controller():

    def __init__(self):
        sys.excepthook = self.exceptionHook

        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))
        # app.setWindowIcon(QIcon("taskbar_icon.png"))
        self.subControllers = [
            UnmixTabController(self),
            LeadLossTabController(self)
        ]

        self.mainWindow = GUI(self)
        sys.exit(app.exec_())

    def exceptionHook(self, exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        QMessageBox.critical(None, "Error", str(value))

class GUI(QDialog):

    def __init__(self, controller):
        super().__init__()

        self.left = 10
        self.top = 10
        self.width = 1220
        self.height = 500

        self.setWindowTitle('Concordia')
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(self.windowFlags() & Qt.WindowMaximizeButtonHint)

        tabWidget = QTabWidget()
        for subController in controller.subControllers:
            tabWidget.addTab(subController.view, subController.name)
        tabWidget.setCurrentWidget(controller.subControllers[0].view)
        layout = QHBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        self.show()
        #self.showMaximized()

if __name__ == '__main__':
    controller = Controller()
