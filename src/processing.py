from typing import List, Optional

from scipy.optimize import root_scalar

from model.reconstructedAge import ReconstructedAge
from model.settings.calculation import CalculationSettings
from model.spot import SpotInputData, Spot, SpotOutputData
from utils import errorUtils, calculations
from utils.asynchronous import ProcessSignals
from utils.calculations import age_from_u238pb206, pb207pb206_from_age, u238pb206_from_age


def process_spots(signals: ProcessSignals, spots: List[Spot], settings: CalculationSettings) -> None:
    for i, spot in enumerate(spots):
        if signals.halt():
            signals.cancelled()
            return

        if spot.has_invalid_inputs():
            continue

        output_data = process_spot(spot.inputs, settings)
        signals.progress((i + 1) / len(spots), i, output_data)
    signals.completed(None)


def process_spot(inputs: SpotInputData, settings: CalculationSettings) -> SpotOutputData:
    rim_age = errorUtils.ufloat(inputs.rim_age_value, inputs.rim_age_st_dev) * 10 ** 6
    mixed_u_pb = errorUtils.ufloat(inputs.mixed_u_pb_value, inputs.mixed_u_pb_st_dev)
    mixed_pb_pb = errorUtils.ufloat(inputs.mixed_pb_pb_value, inputs.mixed_pb_pb_st_dev)

    rim_u_pb = calculations.u238pb206_from_age(rim_age)
    rim_pb_pb = calculations.pb207pb206_from_age(rim_age)
    rim_u_pb_value = errorUtils.value(rim_u_pb)
    rim_u_pb_st_dev = errorUtils.stddev(rim_u_pb)
    rim_pb_pb_value = errorUtils.value(rim_pb_pb)
    rim_pb_pb_st_dev = errorUtils.stddev(rim_pb_pb)

    reconstructed_age = calculate_discordant_age(
        rim_u_pb, rim_pb_pb,
        mixed_u_pb, mixed_pb_pb,
        settings.output_error_sigmas,
        settings.output_error_type
    )

    if reconstructed_age is None:
        return SpotOutputData(
            rim_u_pb_value,
            rim_u_pb_st_dev,
            rim_pb_pb_value,
            rim_pb_pb_st_dev,
        )

    t, u, p = reconstructed_age.get_values()

    alpha_damage = calculations.alpha_damage(inputs.u_concentration_ppm, inputs.th_concentration_ppm, t)
    metamict_score = calculations.metamict_score(alpha_damage)
    rim_age_precision_score = calculations.rim_age_precision_score(inputs.rim_age_value, inputs.rim_age_st_dev * 2)
    if u and p:
        core_to_rim_score = calculations.core_to_rim_score(
            rim_u_pb_value,
            rim_pb_pb_value,
            inputs.mixed_u_pb_value,
            inputs.mixed_pb_pb_value,
            u,
            p
        )
    else:
        core_to_rim_score = 0

    total_score = metamict_score * rim_age_precision_score * core_to_rim_score
    rejected = total_score < 0.5

    return SpotOutputData(
        rim_u_pb_value,
        rim_u_pb_st_dev,
        rim_pb_pb_value,
        rim_pb_pb_st_dev,
        reconstructed_age,
        metamict_score,
        rim_age_precision_score,
        core_to_rim_score,
        total_score,
        rejected
    )


def calculate_discordant_age(x1, y1, x2, y2, output_error_sigmas, output_error_type) -> Optional[ReconstructedAge]:
    if x1 <= x2:
        return None

    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1

    lower_limit = age_from_u238pb206(min(errorUtils.value(x1), errorUtils.value(x2)))
    upper_limit = 5 * (10 ** 9)

    def solve_for_t(error_sign):
        def func(t):
            curve_pb207pb206_value = pb207pb206_from_age(t)
            line_pb207pb206 = m * u238pb206_from_age(t) + c
            line_pb207pb206_value = errorUtils.value(line_pb207pb206) + error_sign * output_error_sigmas * errorUtils.stddev(
                line_pb207pb206)
            return curve_pb207pb206_value - line_pb207pb206_value

        v1 = func(lower_limit)
        v2 = func(upper_limit)
        if (v1 > 0 and v2 > 0) or (v1 < 0 and v2 < 0):
            return None

        result = root_scalar(func, bracket=(lower_limit, upper_limit))

        t = result.root
        x = u238pb206_from_age(t)
        y = pb207pb206_from_age(t)
        return t, x, y

    value = solve_for_t(0)
    if value is None:
        return None

    lower_bound = solve_for_t(-1)
    upper_bound = solve_for_t(1)

    return ReconstructedAge(value, lower_bound, upper_bound, output_error_type)