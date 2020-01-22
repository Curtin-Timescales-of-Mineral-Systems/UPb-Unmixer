import csv
import math
import calculations
import os

from config import *
import error_propagation
import utils

def run(input_file, output_file, save_figures):
    rows = _read_input(input_file)

    print("Reading input data from: " + os.path.abspath(input_file))
    print("Writing output data to: " + os.path.abspath(output_file))

    if save_figures:
        figure_dir = os.path.splitext(output_file)[0]
        if not os.path.exists(figure_dir):
            os.makedirs(figure_dir)
        print("Writing output figures to: " + os.path.abspath(figure_dir))
    else:
        figure_dir = None

    utils.print_progress_bar(0, len(rows))
    for i, row in enumerate(rows[1:]):
        utils.print_progress_bar(i+1, len(rows))
        try:
            _perform_calculations(i+1, row, figure_dir)
        except ValueError as e:
            utils.print_warning("\rIgnoring row " + str(i) + ": " + str(e))
    utils.print_progress_bar(len(rows), len(rows))

    error_strings = ["-" + utils.ERROR_STR_OUTPUT, "+" + utils.ERROR_STR_OUTPUT]
    rows[0].extend(["Recon. age"] + error_strings + ["Recon. U238/Pb206"] + error_strings + ["Recon. Pb207/Pb206"] + error_strings)
    _write_output(output_file, rows)

def _read_input(input_file):
    with open(input_file, newline='') as csvfile:
        return [row for row in csv.reader(csvfile, delimiter=CSV_DELIMITER, quotechar='|')]


def _write_output(output_file, rows):
    with open(output_file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            spamwriter.writerow(row)

def _perform_calculations(row_number, row, figure_dir=None):
    rim_age_value = _parse(COLUMN_RIM_AGE, "Rim age", row, row_number)
    mixed_U238Pb206_value = _parse(COLUMN_MIXED_POINT_U238Pb206, "mixed point U238/Pb206", row, row_number)
    mixed_Pb207Pb206_value = _parse(COLUMN_MIXED_POINT_Pb207Pb206, "mixed point Pb207/Pb206", row, row_number)
    
    rim_age_raw_error = _parse(COLUMN_RIM_AGE_ERROR, "Rim age error", row, row_number)
    mixed_U238Pb206_raw_error = _parse(COLUMN_MIXED_POINT_U238Pb206_ERROR, "mixed point U238/Pb206 error", row, row_number)
    mixed_Pb207Pb206_raw_error = _parse(COLUMN_MIXED_POINT_Pb207Pb206_ERROR, "mixed point Pb207/Pb206 error", row, row_number)

    rim_age_stddev = utils.convert_to_stddev(rim_age_value, rim_age_raw_error, ERROR_TYPE_RIM_AGE, SIGMAS_RIM_AGE_ERROR)
    mixed_U238Pb206_stddev = utils.convert_to_stddev(mixed_U238Pb206_value, mixed_U238Pb206_raw_error, ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)
    mixed_Pb207Pb206_stddev = utils.convert_to_stddev(mixed_Pb207Pb206_value, mixed_Pb207Pb206_raw_error, ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)

    rim_age = error_propagation.ufloat(rim_age_value, rim_age_stddev)* (10**6)
    mixed_U238Pb206 = error_propagation.ufloat(mixed_U238Pb206_value, mixed_U238Pb206_stddev)
    mixed_Pb207Pb206 = error_propagation.ufloat(mixed_Pb207Pb206_value, mixed_Pb207Pb206_stddev)

    rim_U238Pb206 = calculations.u238pb206_from_age(rim_age)
    rim_Pb207Pb206 = calculations.pb207pb206_from_age(rim_age)

    value, value_min, value_max = calculations.reconstruct_age(
        rim_U238Pb206, rim_Pb207Pb206,
        mixed_U238Pb206, mixed_Pb207Pb206
    )

    new_data = ["n/a"] * 9
    if value is not None:
        new_data[0] = value[0] / (10 **6)
        new_data[3] = value[1]
        new_data[6] = value[2]
    
        if value_min is not None and value_max is not None:
            new_data[1] = new_data[0]-(value_min[0] / (10 **6))
            new_data[4] = new_data[3]-value_max[1]
            new_data[7] = new_data[6]-value_min[2]

            new_data[2] = (value_max[0] / (10 **6))-new_data[0]
            new_data[5] = value_min[1]-new_data[3]
            new_data[8] = value_max[2]-new_data[6]

    for i,v in enumerate(new_data):
        if isinstance(v, float):
            new_data[i] = utils.round_to_sf(v, OUTPUT_SIGNIFICANT_FIGURES)

    if figure_dir:
        import interactive_mode
        sample_name = row[utils.get_column_number(COLUMN_SAMPLE_NAME)]
        file_name = figure_dir + "/" + sample_name
        interactive_mode.plot_and_save(rim_U238Pb206, rim_Pb207Pb206, mixed_U238Pb206, mixed_Pb207Pb206, value, value_min, value_max, sample_name, file_name)

    row.extend(new_data)



#######################
## Utility functions ##
#######################

def _parse(column_ref, column_name, row, row_number):
    column_number = utils.get_column_number(column_ref)
    string = row[column_number]
    try:
        return float(string)
    except:
        raise ValueError("Invalid value '" + string + "' for '" + column_name + "' in row " + str(row_number) + " column " + str(column_number))

