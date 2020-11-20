import csv
from enum import Enum

from PyQt5.QtCore import QRegExp

from model.settings.columnIndex import convert_column_ref
from utils.config import *


#####################
# Column references #
#####################

from utils.exception import ExpectedException



#######################
# Reading and writing #
#######################

def read_input(input_file, settings):
    with open(input_file, newline='', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=settings.csv_delimiter, quotechar='|')
        try:
            lines = [line for line in reader]
        except UnicodeDecodeError:
            raise ExpectedException("The input file appears to have unicode characters in that cannot be decoded. "
                                    "Please remove these characters and try again.")

        if settings.csv_has_headers:
            rows = lines[1:]
            headers = lines[0]
        else:
            rows = lines
            headers = None

    largest_column_number_asked_for = settings.get_largest_column_asked_for()
    largest_column_ref_asked_for = convert_column_ref(largest_column_number_asked_for + 1,
                                                      settings.column_reference_type,
                                                      False)
    for line in lines:
        if largest_column_number_asked_for >= len(line):
            largest_column_ref_available = convert_column_ref(len(line),
                                                              settings.column_reference_type,
                                                              False)

            raise ExpectedException(
                "Invalid column reference. Asked for column " + str(largest_column_ref_asked_for) +
                " but the CSV file only goes up to column " + str(largest_column_ref_available) + "."
            )

    return headers, rows


def write_output(headers, rows, output_file) -> None:
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)