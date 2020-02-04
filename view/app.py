import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot

import config

from view.graphPanel import GraphPanel
from view.dataPanel import DataPanel
from view.statusBar import StatusBarWidget

from model.settings import Settings

import sys

class App(QDialog):

    def __init__(self):
        super().__init__()
        sys.excepthook = self.exceptionHook

        self.settings = Settings.loadSettings()

        self.title = 'Concordia'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar = StatusBarWidget()
        self.graphPanel = GraphPanel()
        self.dataPanel = DataPanel(self)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.graphPanel)
        splitter.addWidget(self.dataPanel)
        splitter.setSizes([10000,10000])
        splitter.setContentsMargins(10,10,10,10)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(splitter, 1)
        windowLayout.addWidget(self.statusBar, 0)
        self.setLayout(windowLayout)

        self.showMaximized()

    def exceptionHook(self, exctype, value, traceback):
        print(traceback)
        QMessageBox.critical(None, "Error", str(value))
        sys.__excepthook__(exctype, value, traceback)

    def _cheat(self):
        self.dataPanel.inputFile = "/home/matthew/Dropbox/Academia/Code/Python/UnmixConcordia/data/test.csv"
        self.dataPanel._endCSVImport(True, self.dataPanel._csvImport())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setWindowIcon(QIcon("taskbar_icon.png"))
    ex = App()
    sys.exit(app.exec_())