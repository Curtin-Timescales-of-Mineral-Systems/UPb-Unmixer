from scipy.optimize import root_scalar

import model.errors as errors

###############
## Constants ##
###############

U238_DECAY_CONSTANT = 1.54*(10**-10)
U235_DECAY_CONSTANT = 9.72*(10**-10)
U238U235_RATIO = 137.818

##################
## Calculations ##
##################

def age_from_u238pb206(u238pb206):
    return errors.log(1/u238pb206 + 1)/U238_DECAY_CONSTANT

def pb206u238_from_age(age):
    return errors.exp(U238_DECAY_CONSTANT * age) - 1

def u238pb206_from_age(age):
    return 1/(pb206u238_from_age(age))

def pb207u235_from_age(age):
    return errors.exp(U235_DECAY_CONSTANT * age) - 1

def pb207pb206_from_age(age):
    pb207u235 = pb207u235_from_age(age)
    u238pb206 = u238pb206_from_age(age)
    return pb207u235*(1/U238U235_RATIO)*u238pb206

def pb207pb206_from_u238pb206(u238pb206):
    age = age_from_u238pb206(u238pb206)
    return pb207pb206_from_age(age)

def reconstruct_age(x1, y1, x2, y2, outputSigmas):
    m = (y2 - y1)/(x2 - x1)
    c = y1 - m*x1

    lower_limit = age_from_u238pb206(min(errors.value(x1),errors.value(x2)))
    upper_limit = 5*(10**9)

    def solve_for_t(error_sign):
        def func(t):
            curve_pb207pb206_value = pb207pb206_from_age(t)
            line_pb207pb206 = m*u238pb206_from_age(t) + c
            line_pb207pb206_value = errors.value(line_pb207pb206) + error_sign*outputSigmas*errors.stddev(line_pb207pb206)
            return curve_pb207pb206_value - line_pb207pb206_value

        v1 = func(lower_limit)
        v2 = func(upper_limit)
        if (v1 > 0 and v2 > 0) or (v1 < 0 and v2 < 0):
            return None
        
        result = root_scalar(func, bracket=(lower_limit, upper_limit))

        t = result.root
        x = u238pb206_from_age(t)
        y = pb207pb206_from_age(t)
        return (t, x, y)

    value = solve_for_t(0)
    lower_bound = solve_for_t(-1)
    upper_bound = solve_for_t(1)

    return (value, lower_bound, upper_bound)