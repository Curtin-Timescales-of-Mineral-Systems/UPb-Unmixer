######################
## General settings ##
######################

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
MONTE_CARLO_SAMPLES = 10,000

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


##########################
## Interactive settings ##
##########################

## Note that the values for the errors in this section are all assumed to be 1 sigma
## and then converted according to the settings at the top

DEFAULT_VALUE_RIM_AGE = 500
DEFAULT_VALUE_RIM_AGE_ERROR = 25
DEFAULT_VALUE_MIXED_POINT_U238Pb206 = 7
DEFAULT_VALUE_MIXED_POINT_U238Pb206_ERROR = 0.5
DEFAULT_VALUE_MIXED_POINT_Pb207Pb206 = 0.1
DEFAULT_VALUE_MIXED_POINT_Pb207Pb206_ERROR = 0.01

MIN_VALUE_RIM_AGE = 300
MIN_VALUE_RIM_AGE_ERROR = 0
MIN_VALUE_MIXED_POINT_U238Pb206 = 2
MIN_VALUE_MIXED_POINT_U238Pb206_ERROR = 0.0
MIN_VALUE_MIXED_POINT_Pb207Pb206 = 0.08
MIN_VALUE_MIXED_POINT_Pb207Pb206_ERROR = 0.00

MAX_VALUE_RIM_AGE = 2500
MAX_VALUE_RIM_AGE_ERROR = 500
MAX_VALUE_MIXED_POINT_U238Pb206 = 12
MAX_VALUE_MIXED_POINT_U238Pb206_ERROR = 1
MAX_VALUE_MIXED_POINT_Pb207Pb206 = 0.18
MAX_VALUE_MIXED_POINT_Pb207Pb206_ERROR = 0.02

##################
## GUI settings ##
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
COLOUR_CONCORDIA_CURVE = 'b'
COLOUR_RIM_AGE = 'y'
COLOUR_MIXED_POINT = 'g'
COLOUR_RECONSTRUCTED_AGE = 'r'