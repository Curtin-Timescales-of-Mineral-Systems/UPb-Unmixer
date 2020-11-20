from enum import Enum

from PyQt5.QtCore import QRegExp


class ColumnIndex:
    def __init__(self, initial_value: int):
        self._value: int = initial_value

    def set_int_value(self, value: int) -> None:
        self._value = value

    def set_str_value(self, value: str) -> None:
        self._value = column_letters_to_number(value)

    def get_int_value(self) -> int:
        return self.value

    def get_str_value(self) -> str:
        return column_number_to_letters(self._value)


def _letter_to_number(letter):
    return ord(letter) - 64


def _number_to_letter(number):
    return chr(number + 64)


def column_number_to_letters(number, zeroIndexed):
    if isinstance(number, str):
        return number

    if zeroIndexed:
        number += 1

    letters = ""
    while True:
        letters = _number_to_letter(number % 26) + letters
        number = number // 26
        if number == 0:
            return letters


def column_letters_to_number(letters, zero_indexed):
    if isinstance(letters, int):
        return letters

    if isinstance(letters, str):
        letters = letters.replace(" ", "")
        number = 0
        for i, char in enumerate(letters):
            digit = _letter_to_number(char)
            exponent = len(letters) - i - 1
            number += digit * (26 ** exponent)
        if zero_indexed:
            number -= 1
        return number

    raise Exception("Unexpected value " + letters)


def convert_column_ref(ref, column_ref_type, zero_indexed):
    if column_ref_type is ColumnReferenceType.NUMBERS:
        return column_letters_to_number(ref, zero_indexed)
    if column_ref_type is ColumnReferenceType.LETTERS:
        return column_number_to_letters(ref, zero_indexed)
    raise Exception("Unexpected ColumnReferenceType: " + str(column_ref_type))


class ColumnReferenceType(Enum):
    LETTERS = "Letters"
    NUMBERS = "Numbers"


COLUMN_REFERENCE_TYPE_REGEXES = {
    ColumnReferenceType.LETTERS: QRegExp("[a-zA-Z]+"),
    ColumnReferenceType.NUMBERS: QRegExp("[1-9]([0-9]*)")
}
