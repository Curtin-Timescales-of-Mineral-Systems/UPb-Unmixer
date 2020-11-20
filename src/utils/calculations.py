import math
from typing import Union, Optional

from scipy.optimize import root_scalar
from soerp import UncertainVariable

import utils.errorUtils as errorUtils
from model.reconstructedAge import ReconstructedAge

#############
# Constants #
#############

U238_DECAY_CONSTANT = 1.55125 * (10 ** -10)
U235_DECAY_CONSTANT = 9.8485 * (10 ** -10)
TH232_DECAY_CONSTANT = 0.49475 * (10 ** -10)

U238U235_RATIO = 137.818
AVOGADRO_NUMBER = 6.022E+23
U_ATOMIC_WEIGHT = 238.029
TH_ATOMIC_WEIGHT = 232.0381


##############
# Geological #
##############

def age_from_u238pb206(u238pb206: Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    return errorUtils.log(1 / u238pb206 + 1) / U238_DECAY_CONSTANT


def age_from_pb207pb206(pb207pb206: Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    return root_scalar(lambda t: pb207pb206_from_age(t) - pb207pb206, x0=9 ** 10, bracket=[1, 10 ** 10]).root


def pb206u238_from_age(age: Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    return errorUtils.exp(U238_DECAY_CONSTANT * age) - 1


def u238pb206_from_age(age: Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    return 1 / (pb206u238_from_age(age))


def pb207u235_from_age(age :Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    return errorUtils.exp(U235_DECAY_CONSTANT * age) - 1


def pb207pb206_from_age(age :Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    pb207u235 = pb207u235_from_age(age)
    u238pb206 = u238pb206_from_age(age)
    return pb207u235 * (1 / U238U235_RATIO) * u238pb206


def pb207pb206_from_u238pb206(u238pb206: Union[float, UncertainVariable]) -> Union[float, UncertainVariable]:
    age = age_from_u238pb206(u238pb206)
    return pb207pb206_from_age(age)


def alpha_damage(u_ppm: float, th_ppm: float, age_a: float) -> float:
    """
    Calculates the alpha damage using U & Th content and age. Based on:
    Murakami et al., 1991, Alpha-decay event damage in zircon, American Mineralogist
    v.76, p.1510-1532.
    """
    avogadro_constant = AVOGADRO_NUMBER / (10 ** 18)
    uranimum_mass = (u_ppm/1000000) / U_ATOMIC_WEIGHT
    thorium_mass = (th_ppm/1000000) / TH_ATOMIC_WEIGHT
    contrib238 = 8 * ((uranimum_mass * 0.9928 * avogadro_constant) / 1000) * pb206u238_from_age(age_a)
    contrib235 = 7 * ((uranimum_mass * 0.0072 * avogadro_constant) / 1000) * pb207u235_from_age(age_a)
    contrib232 = 6 * ((thorium_mass * avogadro_constant) / 1000) * (errorUtils.exp(age_a * TH232_DECAY_CONSTANT) - 1)
    return (contrib238 + contrib235 + contrib232) * (10 ** -15)


def metamict_score(alpha_damage_score: float) -> float:
    """
    Function returns metamict stage 1, 2 or 3 depending on input alpha value. Based on:
    Murakami et al., 1991, Alpha-decay event damage in zircon,
    American Mineralogist, v.76, p.1510-1532.
    """

    if alpha_damage_score < 3:
        return 1
    if alpha_damage_score < 8:
        return 0.5
    return 0


def core_to_rim_score(rimUPb: float,
                      rimPbPb: float,
                      mixedUPb: float,
                      mixedPbPb: float,
                      reconstructedUPb: float,
                      reconstructedPbPb: float) -> float:
    rim_distance = math.hypot(rimUPb - reconstructedUPb, rimPbPb - reconstructedPbPb)
    core_distance = math.hypot(rimUPb - mixedUPb, rimPbPb - mixedPbPb)
    core_to_rim_ratio = core_distance / rim_distance

    if core_to_rim_ratio >= 0.8:
        return 1
    if core_to_rim_ratio >= 0.05:
        return 0.5 + 0.5 * (core_to_rim_ratio - 0.05) / 0.75
    return 0.5


def rim_age_precision_score(rim_age: float, rim_age_error: float) -> float:
    precision = rim_age_error / rim_age
    if precision < 0.05:
        return 1
    if precision < 0.2:
        return 0.5 + 0.5 * (0.2 - precision) / 0.15
    return 0.5


###########
# General #
###########

def convert_to_stddev(value, error, form, sigmas):
    if form == "Percentage":
        error = (error / 100.0) * value
    return error / sigmas


def convert_from_stddev_with_sigmas(value, error, form, sigmas):
    res = error * sigmas
    if form == "Percentage":
        return 100.0 * res / value
    return res


def convert_from_stddev_without_sigmas(value, error, form):
    if form == "Percentage":
        return 100.0 * error / value
    return error
