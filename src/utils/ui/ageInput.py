from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QLabel


class AgeInput(QWidget):

    def __init__(self, validation, defaultValue):
        super().__init__()

        self.lineEdit = QLineEdit(str(defaultValue))
        self.lineEdit.textChanged.connect(validation)

        unitsLabel = QLabel("Ma")

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.lineEdit)
        layout.addWidget(unitsLabel)

        self.setLayout(layout)

    def getAge(self):
        return float(self.lineEdit.text())
