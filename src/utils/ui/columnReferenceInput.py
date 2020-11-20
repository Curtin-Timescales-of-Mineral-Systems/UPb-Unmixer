from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout

from model.settings import columnIndex
from model.settings.columnIndex import ColumnReferenceType
from utils.ui import uiUtils


class ColumnReferenceInput(QWidget):
    width = 30

    def __init__(self, validation, reference_type: ColumnReferenceType, default_value: int):
        super().__init__()

        letter_default = columnIndex.column_number_to_letters(default_value, zeroIndexed=True)
        number_default = str(default_value + 1)

        self.number_widget = QLineEdit(number_default)
        self.number_widget.setFixedWidth(self.width)
        self.number_widget.setAlignment(Qt.AlignCenter)
        self.number_widget.textChanged.connect(validation)
        self.number_widget.setVisible(reference_type is ColumnReferenceType.NUMBERS)
        uiUtils.attachValidator(self.number_widget, columnIndex.COLUMN_REFERENCE_TYPE_REGEXES[ColumnReferenceType.NUMBERS])

        self.letters_widget = QLineEdit(letter_default)
        self.letters_widget.setFixedWidth(self.width)
        self.letters_widget.setAlignment(Qt.AlignCenter)
        self.letters_widget.textChanged.connect(self._convert_to_upper_case)
        self.letters_widget.textChanged.connect(validation)
        self.letters_widget.setVisible(reference_type is ColumnReferenceType.LETTERS)
        uiUtils.attachValidator(self.letters_widget, columnIndex.COLUMN_REFERENCE_TYPE_REGEXES[ColumnReferenceType.LETTERS])

        layout = QHBoxLayout()
        layout.addWidget(self.number_widget)
        layout.addWidget(self.letters_widget)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.current_reference_type = reference_type

    def _convert_to_upper_case(self):
        self.letters_widget.setText(self.letters_widget.text().upper())

    def set_column_reference_type(self, new_reference_type: ColumnReferenceType):
        if self.current_reference_type == new_reference_type:
            return

        if self.current_reference_type is ColumnReferenceType.LETTERS:
            old_text = self.letters_widget.text()
            new_text = str(columnIndex.column_letters_to_number(old_text, zero_indexed=False))
            self.number_widget.setText(new_text)
        else:
            old_text = self.number_widget.text()
            new_text = columnIndex.column_number_to_letters(int(old_text), zeroIndexed=False)
            self.letters_widget.setText(new_text)

        self.letters_widget.setVisible(new_reference_type is ColumnReferenceType.LETTERS)
        self.number_widget.setVisible(new_reference_type is ColumnReferenceType.NUMBERS)

        self.current_reference_type = new_reference_type

    def get_column_index(self) -> int:
        if self.current_reference_type is ColumnReferenceType.LETTERS:
            text = self.letters_widget.text()
            if not text:
                return None
            return columnIndex.column_letters_to_number(text, zero_indexed=True)

        if self.current_reference_type is ColumnReferenceType.NUMBERS:
            text = self.number_widget.text()
            if not text:
                return None
            return int(text) - 1

        raise Exception("Unknown ColumnReferenceType: " + str(self.current_reference_type))
