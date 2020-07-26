import multiprocessing
import sys
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QMessageBox, QApplication, QStyleFactory

from controller.controller import UnmixTabController
from utils import config
from utils.exception import ExpectedException


class UPbUnmixerApplication:

    def __init__(self):
        # Necessary for building executable with Pyinstaller correctly on Windows
        # (see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing)
        multiprocessing.freeze_support()

    def exceptionHook(self, exctype, value, tb):
        if isinstance(value, ExpectedException):
            QMessageBox.critical(None, "Error", str(value))
            return

        sys.__excepthook__(exctype, value, tb)
        error = str(value) + "\n" + "".join(traceback.format_tb(tb))

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An error occured. Please file a bug report with the details below at 'https://github.com/Curtin-Timescales-of-Mineral-Systems/UPb-Unmixer/issues'")
        msg.setWindowTitle("Error")
        msg.setDetailedText(error)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def createGUI(self):
        # Reroute exceptions to display a message box to the user
        sys.excepthook = self.exceptionHook

        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon(self.getIcon()))

        self.mainWindow = GUI(self)
        sys.exit(app.exec_())

    def getControllers(self):
        return [self.createController()]

    @staticmethod
    def getTitle():
        return config.U_PB_UNMIXER_TITLE

    @staticmethod
    def getVersion():
        return config.VERSION

    @staticmethod
    def getIcon():
        return "../resources/icon.ico"

    @staticmethod
    def createController():
        return UnmixTabController()

class GUI(QDialog):

    def __init__(self, application):
        super().__init__()

        self.left = 10
        self.top = 10
        self.width = 1220
        self.height = 500

        title = application.getTitle()
        version = application.getVersion()
        controllers = application.getControllers()

        self.setWindowTitle(title + " (v" + version + ")")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(self.windowFlags() & Qt.WindowMaximizeButtonHint)

        if len(controllers) > 1:
            widget = QTabWidget()
            for controller in controllers:
                widget.addTab(controller.view, controller.name)
            widget.setCurrentWidget(controllers[0].view)
        else:
            widget = controllers[0].view

        layout = QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)
        self.showMaximized()


if __name__ == '__main__':
    app = UPbUnmixerApplication()
    app.createGUI()
