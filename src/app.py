from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *

import multiprocessing

from tabs.unmix.controller import UnmixTabController
from tabs.leadLoss.controller import LeadLossTabController

import sys

VERSION = "1.0"

class Controller():

    def __init__(self):
        sys.excepthook = self.exceptionHook

        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon("resources/icon.png"))

        self.subControllers = [
            UnmixTabController(self),
            #LeadLossTabController(self)
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

        self.setWindowTitle('U-Pb Unmixer ' + "(v" + VERSION + ")")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(self.windowFlags() & Qt.WindowMaximizeButtonHint)

        """
        tabWidget = QTabWidget()
        for subController in controller.subControllers:
            tabWidget.addTab(subController.view, subController.name)
        tabWidget.setCurrentWidget(controller.subControllers[0].view)
        """
        layout = QVBoxLayout()
        layout.addWidget(controller.subControllers[0].view)
        self.setLayout(layout)

        self.showMaximized()

if __name__ == '__main__':
    # Necessary for building executable with Pyinstaller correctly on Windows
    # (see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing)
    multiprocessing.freeze_support()

    controller = Controller()
