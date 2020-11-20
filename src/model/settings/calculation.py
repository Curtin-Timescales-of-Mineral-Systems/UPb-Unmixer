from utils import string
from model.settings.type import SettingsType


class CalculationSettings:
    """
    User settings for the calculation of the reconstructed rim ages.
    """
    KEY = SettingsType.CALCULATION

    @staticmethod
    def _get_headers(outputErrorSigmas: int, outputErrorType: str, useUnicode: bool) -> [str]:
        error = string.get_error_str(outputErrorSigmas, outputErrorType, useUnicode)
        minus_error = "-" + error
        plus_error = "+" + error

        return [
            "Reconstructed age (Ma)",
            minus_error,
            plus_error,
            "Reconstructed " + string.getUPbStr(useUnicode),
            minus_error,
            plus_error,
            "Reconstructed " + string.getPbPbStr(useUnicode),
            minus_error,
            plus_error,
            "Metamict score",
            "Precision score",
            "Core:rim score",
            "Total score",
        ]

    @staticmethod
    def get_default_headers_for_display() -> [str]:
        return CalculationSettings._get_headers(2, "Absolute", True)

    def __init__(self):
        super().__init__()

        self.output_error_sigmas: int = 2
        self.output_error_type: str = "Absolute"

    def get_output_error(self, value: float, diff: float) -> float:
        if self.output_error_type == "Absolute":
            return diff
        return (diff / value) * 100.0

    def get_headers_for_display(self) -> [str]:
        return CalculationSettings._get_headers(self.output_error_sigmas, self.output_error_type, True)

    def get_headers_for_export(self) -> [str]:
        return CalculationSettings._get_headers(self.output_error_sigmas, self.output_error_type, False)

    def validate(self) -> [str]:
        return None
