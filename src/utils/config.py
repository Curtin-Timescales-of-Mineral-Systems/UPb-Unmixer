from PyQt5.QtGui import QColor

####################
# General settings #
####################

TITLE = "U-Pb Unmixer"
VERSION = "2.0"

################
# CSV settings #
################

# Delimiter
CSV_DELIMITER = ","

################
# GUI settings #
################

# Graph labels
LABEL_U238Pb206 = "238U/206Pb"
LABEL_U238Pb206_ERROR = LABEL_U238Pb206 + " error"
LABEL_Pb207Pb206 = "207Pb/206Pb"
LABEL_Pb207Pb206_ERROR = LABEL_Pb207Pb206 + " error"

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
