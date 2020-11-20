import unittest

from model.settings.imports.columnReference import column_letters_to_number
from utils.csvUtils import *


class CSVUtilsMethods(unittest.TestCase):

    def testColumnLettersToNumbers(self):
        self.assertEqual(column_letters_to_number("A", False), 1)
        self.assertEqual(column_letters_to_number("B", False), 2)
        self.assertEqual(column_letters_to_number("AA", False), 27)
        self.assertEqual(column_letters_to_number("AB", False), 28)
        self.assertEqual(column_letters_to_number("BA", False), 53)

        self.assertEqual(column_letters_to_number("A", True), 0)
        self.assertEqual(column_letters_to_number("B", True), 1)
        self.assertEqual(column_letters_to_number("AA", True), 26)
        self.assertEqual(column_letters_to_number("AB", True), 27)
        self.assertEqual(column_letters_to_number("BA", True), 52)

    def testColumnNumberToLetters(self):
        self.assertEqual(column_number_to_letters(1, False), "A")
        self.assertEqual(column_number_to_letters(2, False), "B")
        self.assertEqual(column_number_to_letters(27, False), "AA")
        self.assertEqual(column_number_to_letters(28, False), "AB")
        self.assertEqual(column_number_to_letters(53, False), "BA")

        self.assertEqual(column_number_to_letters(0, True), "A")
        self.assertEqual(column_number_to_letters(1, True), "B")
        self.assertEqual(column_number_to_letters(26, True), "AA")
        self.assertEqual(column_number_to_letters(27, True), "AB")
        self.assertEqual(column_number_to_letters(52, True), "BA")


if __name__ == '__main__':
    unittest.main()
