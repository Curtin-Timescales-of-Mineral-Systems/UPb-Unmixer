from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QWidget, QLabel


class AbstractHelpDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.getTitle() + " help")

        inputsLabel = QLabel(self.getInputsHelpText())
        inputsLabel.title = "Inputs"

        processingLabel = QLabel(self.getProcessingHelpText())
        processingLabel.title = "Processing"

        outputsLabel = QLabel(self.getOutputsHelpText())
        outputsLabel.title = "Outputs"

        tabWidget = QTabWidget()
        for label in [inputsLabel, processingLabel, outputsLabel]:
            label.setTextFormat(Qt.RichText)
            label.setWordWrap(True)
            layout = QVBoxLayout()
            layout.addWidget(label, 0, Qt.AlignTop)
            widget = QWidget()
            widget.setLayout(layout)
            tabWidget.addTab(widget, label.title)

        layout = QVBoxLayout()
        layout.addWidget(tabWidget)

        self.setLayout(layout)