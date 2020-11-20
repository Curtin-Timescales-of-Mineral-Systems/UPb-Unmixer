from typing import Tuple, Optional


class ReconstructedAge:
    def __init__(self,
                 values: Tuple[float, float, float],
                 min_values: Optional[Tuple[float, float, float]],
                 max_values: Optional[Tuple[float, float, float]],
                 output_error_type: str):
        self._values = list(values)
        self._min_values = list(min_values) if min_values else [None] * 3
        self._max_values = list(max_values) if max_values else [None] * 3

        self.valid = min_values is not None and max_values is not None

        # Swap u_pb values as they are inverted with respect to age
        t1 = self._min_values[1]
        self._min_values[1] = self._max_values[1]
        self._max_values[1] = t1

        self._ages = self._get_values_and_error(0, output_error_type)
        self._u_pb = self._get_values_and_error(1, output_error_type)
        self._pb_pb = self._get_values_and_error(2, output_error_type)

    def get_values(self):
        return self._values

    def get_min_values(self):
        return self._min_values

    def get_max_values(self):
        return self._max_values

    def get_age_ma(self) -> Tuple[float, float, float]:
        return self._ages

    def get_u_pb(self) -> Tuple[float, float, float]:
        return self._u_pb

    def get_pb_pb(self) -> Tuple[float, float, float]:
        return self._pb_pb

    def _get_values_and_error(self, i, output_error_type: str):
        scale = (10 ** -6) if i == 0 else 1

        value = self._values[i]
        if value:
            value *= scale

        min_value = self._min_values[i]
        if min_value:
            min_value = value - scale * min_value
            if output_error_type == "Percentage":
                min_value = 100.0 * min_value / value

        max_value = self._max_values[i]
        if max_value:
            max_value = scale * self._max_values[i] - value
            if output_error_type == "Percentage":
                max_value = 100.0 * max_value / value

        return value, min_value, max_value
