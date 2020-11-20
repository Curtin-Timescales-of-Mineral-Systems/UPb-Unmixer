from enum import Enum


class Column(Enum):
    """
    The different columns read from the input CSV file
    """
    RIM_AGE_VALUE = 0
    RIM_AGE_ERROR = 1
    MIXED_U_PB_VALUE = 2
    MIXED_U_PB_ERROR = 3
    MIXED_PB_PB_VALUE = 4
    MIXED_PB_PB_ERROR = 5
    U_CONCENTRATION = 6
    TH_CONCENTRATION = 7
