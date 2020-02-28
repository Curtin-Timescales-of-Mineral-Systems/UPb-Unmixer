import csv

from config import *
import utils

import model.errors as errors
import model.calculations as calculations


def read_input(input_file, settings):
    with open(input_file, newline='', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=settings.delimiter, quotechar='|')
        lines = [line for line in reader]

        if settings.hasHeaders:
            rows = lines[1:]
            headers = lines[0]
        else:
            rows = lines
            headers = None

    return headers, rows


def write_output(headers, rows, output_file):
    with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row.inputValues + row.outputValues)


def perform_all_calculations(headers, rows, figure_dir, progress_callback):
    error_strings = ["-" + utils.ERROR_STR_OUTPUT, "+" + utils.ERROR_STR_OUTPUT]
    headers.extend(
        ["Recon. age"] + error_strings + ["Recon. U238/Pb206"] + error_strings + ["Recon. Pb207/Pb206"] + error_strings)

    progress_callback(0)
    for i, row in enumerate(rows[1:]):
        progress_callback(i + 1)
        try:
            _perform_calculations(i + 1, row, figure_dir)
        except ValueError as e:
            utils.print_warning("\rIgnoring row " + str(i) + ": " + str(e))
    progress_callback(len(rows))


def _perform_calculations(row_number, row, figure_dir=None):
    rim_age_value = _parse(COLUMN_RIM_AGE, "Rim age", row, row_number)
    mixed_U238Pb206_value = _parse(COLUMN_MIXED_POINT_U238Pb206, "mixed point U238/Pb206", row, row_number)
    mixed_Pb207Pb206_value = _parse(COLUMN_MIXED_POINT_Pb207Pb206, "mixed point Pb207/Pb206", row, row_number)

    rim_age_raw_error = _parse(COLUMN_RIM_AGE_ERROR, "Rim age error", row, row_number)
    mixed_U238Pb206_raw_error = _parse(COLUMN_MIXED_POINT_U238Pb206_ERROR, "mixed point U238/Pb206 error", row,
                                       row_number)
    mixed_Pb207Pb206_raw_error = _parse(COLUMN_MIXED_POINT_Pb207Pb206_ERROR, "mixed point Pb207/Pb206 error", row,
                                        row_number)

    rim_age_stddev = utils.convert_to_stddev(rim_age_value, rim_age_raw_error, ERROR_TYPE_RIM_AGE, SIGMAS_RIM_AGE_ERROR)
    mixed_U238Pb206_stddev = utils.convert_to_stddev(mixed_U238Pb206_value, mixed_U238Pb206_raw_error,
                                                     ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)
    mixed_Pb207Pb206_stddev = utils.convert_to_stddev(mixed_Pb207Pb206_value, mixed_Pb207Pb206_raw_error,
                                                      ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)

    rim_age = errors.ufloat(rim_age_value, rim_age_stddev) * (10 ** 6)
    mixed_U238Pb206 = errors.ufloat(mixed_U238Pb206_value, mixed_U238Pb206_stddev)
    mixed_Pb207Pb206 = errors.ufloat(mixed_Pb207Pb206_value, mixed_Pb207Pb206_stddev)

    rim_U238Pb206 = calculations.u238pb206_from_age(rim_age)
    rim_Pb207Pb206 = calculations.pb207pb206_from_age(rim_age)

    value, value_min, value_max = calculations.reconstruct_age(
        rim_U238Pb206, rim_Pb207Pb206,
        mixed_U238Pb206, mixed_Pb207Pb206
    )

    new_data = ["n/a"] * 9
    if value is not None:
        new_data[0] = value[0] / (10 ** 6)
        new_data[3] = value[1]
        new_data[6] = value[2]

        if value_min is not None and value_max is not None:
            new_data[1] = new_data[0] - (value_min[0] / (10 ** 6))
            new_data[4] = new_data[3] - value_max[1]
            new_data[7] = new_data[6] - value_min[2]

            new_data[2] = (value_max[0] / (10 ** 6)) - new_data[0]
            new_data[5] = value_min[1] - new_data[3]
            new_data[8] = value_max[2] - new_data[6]

    for i, v in enumerate(new_data):
        if isinstance(v, float):
            new_data[i] = utils.round_to_sf(v, OUTPUT_SIGNIFICANT_FIGURES)

    row.extend(new_data)


#######################
## Utility functions ##
#######################

def _parse(column_ref, row, row_number, column_name=None):
    column_number = utils.get_column_number(column_ref)
    string = row[column_number]
    try:
        return float(string)
    except:
        column_text = column_name if column_name else ("column " + column_number)
        raise ValueError(
            "Invalid value '" + string + "' for '" + column_text + "' in row " + str(row_number) + " column " + str(
                column_number))
