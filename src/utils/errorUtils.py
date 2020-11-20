"""
Provides an abstraction over the different methods of error propagation during
mathematical calculations
"""
import soerp as so
import soerp.umath as so_math
import math

error_order = 2


def set_order(order):
    global error_order
    error_order = order


def ufloat(mean, stddev):
    if stddev == 0:
        return float(mean)
    if error_order == 2:
        return so.N(mean, stddev)


def value(x):
    if isinstance(x, float):
        return x
    if error_order == 2:
        return x.mean


def stddev(x):
    if isinstance(x, float):
        return 0
    if error_order == 2:
        return math.sqrt(x.var)


def log(x):
    if isinstance(x, float):
        return math.log(x)
    if error_order == 2:
        return so_math.ln(x)


def exp(x):
    if isinstance(x, float):
        return math.exp(x)
    if error_order == 2:
        return so_math.exp(x)