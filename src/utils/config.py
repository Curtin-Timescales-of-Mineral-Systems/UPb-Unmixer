######################
## General settings ##
######################

# App titles
from PyQt5.QtGui import QColor

U_PB_UNMIXER_TITLE = "U-Pb Unmixer"
VERSION = "1.6"

# Size of the confidence interval -- 1 or 2
SIGMAS_MIXED_POINT_ERROR = 1
SIGMAS_RIM_AGE_ERROR = 1
SIGMAS_OUTPUT_ERROR = 2

# How the error is specified -- either "Absolute" or "Percentage"
ERROR_TYPE_MIXED_POINT = "Percentage"
ERROR_TYPE_RIM_AGE = "Percentage"
ERROR_TYPE_OUTPUT = "Absolute"

# Other
OUTPUT_SIGNIFICANT_FIGURES = 3
CONSTANT_SIGNIFICANT_FIGURES = 6

##################
## CSV settings ##
##################

# Delimiter
CSV_DELIMITER = ","

# Column for the data in the CSV file
# These can either be numbers (with the first column = 0) or letters (A, B, C, up to Z)
COLUMN_MIXED_POINT_U238Pb206 = "H"
COLUMN_MIXED_POINT_U238Pb206_ERROR = "I"
COLUMN_MIXED_POINT_Pb207Pb206 = "J"
COLUMN_MIXED_POINT_Pb207Pb206_ERROR = "K"
COLUMN_RIM_AGE = "S"
COLUMN_RIM_AGE_ERROR = "T"

# Column used to generate the name for the figures when run in CSV mode using the `-f` flag
COLUMN_SAMPLE_NAME = 0

##################
## GUI settingsDialogs ##
##################

# Graph labels
LABEL_RIM_AGE = "Rim age (Ma)"
LABEL_RIM_AGE_ERROR = "Rim age (Ma) error"
LABEL_U238Pb206 = "238U/206Pb"
LABEL_U238Pb206_ERROR = LABEL_U238Pb206 + " error"
LABEL_Pb207Pb206 = "207Pb/206Pb"
LABEL_Pb207Pb206_ERROR = LABEL_Pb207Pb206 + " error"
LABEL_RECONSTRUCTED_AGE = "Reconstructed age"
LABEL_RECONSTRUCTED_AGE_ERROR = "Reconstructed age error"

# Graph colors
Q_INVALID_IMPORT_COLOUR = QColor(255, 0, 0, 27)
Q_INVALID_CALCULATION_COLOUR = QColor(255, 165, 0, 27)
Q_REJECTED_CALCULATION_COLOUR = QColor(230, 230, 0, 27)
Q_VALID_CALCULATION_COLOUR = QColor(0, 255, 0, 27)

COLOUR_CONCORDIA_CURVE = 'b'
INVALID_IMPORT_COLOUR = '#FF0000'
INVALID_CALCULATION_COLOUR = '#FFA500'
REJECTED_CALCULATION_COLOUR = '#E6E600'
VALID_CALCULATION_COLOUR = '#00FF00'