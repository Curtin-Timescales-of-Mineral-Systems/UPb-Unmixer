import math

from config import *

###############
## Functions ##
###############

def print_warning(message):
    print("\033[93m" + message + "\033[0m")

def round_to_sf(x, sf=2):
    if x == 0:
        return 0
    return round(x, sf-int(math.floor(math.log10(abs(x))))-1)

def get_column_number(column_ref):
    if isinstance(column_ref, int):
        return column_ref
    return ord(column_ref.lower()) - 97

def print_progress_bar (iteration, total, prefix = 'Progress', suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def get_error_str(sigmas, type):
	return str(sigmas) + "σ "+ error_symbol(type, brackets=True)

def error_symbol(type, brackets=False):
    if type != "Percentage":
        return ""
    if brackets:
        return "(%)"
    return "%"

def convert_to_stddev(value, error, form, sigmas):
    if form == "Percentage":
        error = (error/100.0) * value
    return error/sigmas

def convert_from_stddev_with_sigmas(value, error, form, sigmas):
    res = error*sigmas
    if form == "Percentage":
        return 100.0*res/value
    return res

def convert_from_stddev_without_sigmas(value, error, form):
    if form == "Percentage":
        return 100.0*error/value
    return error

###############
## Constants ##
###############

ERROR_STR_MIXED_POINT = get_error_str(SIGMAS_MIXED_POINT_ERROR, ERROR_TYPE_MIXED_POINT)
ERROR_STR_RIM_AGE = get_error_str(SIGMAS_RIM_AGE_ERROR, ERROR_TYPE_RIM_AGE)
ERROR_STR_OUTPUT = get_error_str(SIGMAS_OUTPUT_ERROR, ERROR_TYPE_OUTPUT)

ACTUAL_DEFAULT_VALUE_RIM_AGE_ERROR = convert_from_stddev_with_sigmas(
    DEFAULT_VALUE_RIM_AGE, 
    DEFAULT_VALUE_RIM_AGE_ERROR, 
    ERROR_TYPE_RIM_AGE, 
    SIGMAS_RIM_AGE_ERROR
)
ACTUAL_MIN_VALUE_RIM_AGE_ERROR = convert_from_stddev_with_sigmas(
    MIN_VALUE_RIM_AGE, 
    MIN_VALUE_RIM_AGE_ERROR, 
    ERROR_TYPE_RIM_AGE, 
    SIGMAS_RIM_AGE_ERROR
)
ACTUAL_MAX_VALUE_RIM_AGE_ERROR = convert_from_stddev_with_sigmas(
    MAX_VALUE_RIM_AGE, 
    MAX_VALUE_RIM_AGE_ERROR, 
    ERROR_TYPE_RIM_AGE, 
    SIGMAS_RIM_AGE_ERROR
)

ACTUAL_DEFAULT_VALUE_MIXED_POINT_U238Pb206_ERROR = convert_from_stddev_with_sigmas(
    DEFAULT_VALUE_MIXED_POINT_U238Pb206, 
    DEFAULT_VALUE_MIXED_POINT_U238Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)
ACTUAL_MIN_VALUE_MIXED_POINT_U238Pb206_ERROR = convert_from_stddev_with_sigmas(
    MIN_VALUE_MIXED_POINT_U238Pb206, 
    MIN_VALUE_MIXED_POINT_U238Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)
ACTUAL_MAX_VALUE_MIXED_POINT_U238Pb206_ERROR = convert_from_stddev_with_sigmas(
    MAX_VALUE_MIXED_POINT_U238Pb206, 
    MAX_VALUE_MIXED_POINT_U238Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)

ACTUAL_DEFAULT_VALUE_MIXED_POINT_Pb207Pb206_ERROR = convert_from_stddev_with_sigmas(
    DEFAULT_VALUE_MIXED_POINT_Pb207Pb206, 
    DEFAULT_VALUE_MIXED_POINT_Pb207Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)
ACTUAL_MIN_VALUE_MIXED_POINT_Pb207Pb206_ERROR = convert_from_stddev_with_sigmas(
    MIN_VALUE_MIXED_POINT_Pb207Pb206, 
    MIN_VALUE_MIXED_POINT_Pb207Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)
ACTUAL_MAX_VALUE_MIXED_POINT_Pb207Pb206_ERROR = convert_from_stddev_with_sigmas(
    MAX_VALUE_MIXED_POINT_Pb207Pb206, 
    MAX_VALUE_MIXED_POINT_Pb207Pb206_ERROR, 
    ERROR_TYPE_MIXED_POINT, 
    SIGMAS_MIXED_POINT_ERROR
)