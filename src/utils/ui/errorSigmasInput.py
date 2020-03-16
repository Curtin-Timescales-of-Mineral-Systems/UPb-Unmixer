from utils import stringUtils
from utils.ui.radioButtonGroup import RadioButtonGroup


class ErrorSigmasInput(RadioButtonGroup):

    def __init__(self, validation, defaultSigmas):
        default = stringUtils.get_error_sigmas_str(defaultSigmas)
        super().__init__(stringUtils.SIGMA_OPTIONS_STR, validation, default)

    def getSelection(self):
        return stringUtils.SIGMA_OPTIONS_STR.index(super().getSelection()) + 1