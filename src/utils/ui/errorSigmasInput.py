from utils import string
from utils.ui.radioButtons import RadioButtons


class ErrorSigmasInput(RadioButtons):

    def __init__(self, validation, defaultSigmas):
        default = string.get_error_sigmas_str(defaultSigmas)
        super().__init__(string.SIGMA_OPTIONS_STR, validation, default)

    def selection(self):
        return string.SIGMA_OPTIONS_STR.index(super().selection()) + 1