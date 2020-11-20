from typing import Optional

from utils import string


class Cell:

    def is_input_cell(self):
        return isinstance(self, InputCell)

class InputCell(Cell):
    def __init__(self, raw_str: str):
        super().__init__()
        try:
            self.value = float(raw_str)
            self._is_valid = True
            self._display_str = str(string.round_to_sf(self.value, 5))
        except (ValueError, TypeError):
            self.value = None
            self._is_valid = False
            self._display_str = raw_str


    def is_valid(self):
        return self._display_str is not ""

    def get_display_string(self):
        return self._display_str

class OutputCell(Cell):
    def __init__(self, value: Optional[float]):
        super().__init__()
        self._display_str = "" if value is None else str(string.round_to_sf(value, 5))

    def is_input(self):
        return False

    def is_valid(self):
        return self._display_str is ""

    def get_display_string(self):
        return self._display_str

    def get_export_string(self):
        return self._display_str