import math

from scipy.optimize import root_scalar

import utils.errorUtils as errors

###############
## Constants ##
###############
from utils.reconstructedAge import ReconstructedAge

U238_DECAY_CONSTANT = 1.55125 * (10 ** -10)
U235_DECAY_CONSTANT = 9.8485 * (10 ** -10)
TH232_DECAY_CONSTANT = 0.49475 * (10 ** -10)

U238U235_RATIO = 137.818
AVOGADROS_NUMBER = 6.022E+23
U_ATOMIC_WEIGHT = 238.029
TH_ATOMIC_WEIGHT = 232.0381

################
## Geological ##
################

def age_from_u238pb206(u238pb206):
    return errors.log(1 / u238pb206 + 1) / U238_DECAY_CONSTANT


def age_from_pb207pb206(pb207pb206):
    return root_scalar(lambda t: pb207pb206_from_age(t) - pb207pb206, x0=9 ** 10, bracket=[1, 10 ** 10]).root


def pb206u238_from_age(age):
    return errors.exp(U238_DECAY_CONSTANT * age) - 1


def u238pb206_from_age(age):
    return 1 / (pb206u238_from_age(age))


def pb207u235_from_age(age):
    return errors.exp(U235_DECAY_CONSTANT * age) - 1


def pb207pb206_from_age(age):
    pb207u235 = pb207u235_from_age(age)
    u238pb206 = u238pb206_from_age(age)
    return pb207u235 * (1 / U238U235_RATIO) * u238pb206


def pb207pb206_from_u238pb206(u238pb206):
    age = age_from_u238pb206(u238pb206)
    return pb207pb206_from_age(age)


def discordance(u238pb206, pb207pb206):
    uPbAge = age_from_u238pb206(u238pb206)
    pbPbAge = age_from_pb207pb206(pb207pb206)
    return (pbPbAge - uPbAge) / pbPbAge


def concordant_age(u238pb206, pb207pb206):
    """
    def dist(ts):
        global i
        i += 1
        t = ts[0]
        x = u238pb206 - u238pb206_from_age(t)
        y = pb207pb206 - pb207pb206_from_age(t)
        h = math.hypot(x, y)
        print(i, u238pb206, pb207pb206, t, h)
        return h

    solution = minimize(dist, 500*(10**6))
    return solution.x[0]
    """
    return age_from_u238pb206(u238pb206)


def discordant_age(x1, y1, x2, y2, outputSigmas):
    if x1 <= x2:
        return None

    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1

    lower_limit = age_from_u238pb206(min(errors.value(x1), errors.value(x2)))
    upper_limit = 5 * (10 ** 9)

    def solve_for_t(error_sign):
        def func(t):
            curve_pb207pb206_value = pb207pb206_from_age(t)
            line_pb207pb206 = m * u238pb206_from_age(t) + c
            line_pb207pb206_value = errors.value(line_pb207pb206) + error_sign * outputSigmas * errors.stddev(
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
    return ReconstructedAge(value, lower_bound, upper_bound)

def alphaDamage(u_ppm, th_ppm, age):
    avogradro_constant = AVOGADROS_NUMBER / (10 ** 18)
    contrib238 = 8 * (((u_ppm / U_ATOMIC_WEIGHT) * 0.9928) * avogradro_constant) * (errors.exp(age * U238_DECAY_CONSTANT) - 1)
    contrib235 = 7 * (((u_ppm / U_ATOMIC_WEIGHT) * 0.0072) * avogradro_constant) * (errors.exp(age * U235_DECAY_CONSTANT) - 1)
    contrib232 = 6 * ((th_ppm / TH_ATOMIC_WEIGHT) * avogradro_constant) * (errors.exp(age * TH232_DECAY_CONSTANT) - 1)
    alphaDamage = (contrib238 + contrib235 + contrib232)
    return alphaDamage

def metamictScore(alphaDamage):
    if alphaDamage < 3:
        return 1
    if alphaDamage < 8:
        return 0.5
    return 0

def coreToRimScore(rimUPb, rimPbPb, mixedUPb, mixedPbPb, reconstructedUPb, reconstructedPbPb):
    rimDistance = math.hypot(rimUPb - reconstructedUPb, rimPbPb - reconstructedPbPb)
    coreDistance = math.hypot(rimUPb - mixedUPb, rimPbPb - mixedPbPb)
    coreToRimRatio = coreDistance/rimDistance

    if coreToRimRatio >= 0.8:
        return 1
    if coreToRimRatio >= 0.05:
        return 0.5 + 0.5 * (coreToRimRatio - 0.05) / 0.75
    return 0.5

def rimAgePrecisionScore(rim_age, rim_age_error):
    precision = rim_age_error/rim_age
    if precision < 0.05:
        return 1
    if precision < 0.2:
        return 0.5 + 0.5 * (0.2 - precision) / 0.15
    return 0.5

#############
## General ##
#############

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
