"""
The interactive mode for the concordia plotting
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.patches import Ellipse

from config import *
import calculations
import error_propagation as error
import utils

def _generate_basic_concordia_plot():
    plt.xlim(-1,18)
    plt.xlabel(LABEL_U238Pb206)
    plt.ylabel(LABEL_Pb207Pb206)

    maxAge = 4500
    minAge = 200
    xMin = calculations.u238pb206_from_age(maxAge*(10**6))
    xMax = calculations.u238pb206_from_age(minAge*(10**6))

    # Plot concordia curve
    xs = np.arange(xMin,xMax,0.1)
    ys = [calculations.pb207pb206_from_u238pb206(x) for x in xs]
    plt.plot(xs,ys)

    # Plot concordia times
    ts2 = list(range(100, minAge, 100)) + list(range(500, maxAge+1, 500))
    xs2 = [calculations.u238pb206_from_age(t*(10**6)) for t in ts2]
    ys2 = [calculations.pb207pb206_from_age(t*(10**6)) for t in ts2]
    plt.scatter(xs2,ys2)
    for i, txt in enumerate(ts2):
        plt.annotate(str(txt) + " ", (xs2[i], ys2[i]), horizontalalignment="right", verticalalignment="top", fontsize="small")

    # Plotting data
    components = {}
    components["best_fit_line"] = plt.plot([],[],[],[],linestyle='--')[0]
    components["x1_errorline"] = plt.plot([],[],color=COLOUR_RIM_AGE)[0]
    components["y1_errorline"] = plt.plot([],[],color=COLOUR_RIM_AGE)[0]
    components["x2_errorline"] = plt.plot([],[],color=COLOUR_MIXED_POINT)[0]
    components["y2_errorline"] = plt.plot([],[],color=COLOUR_MIXED_POINT)[0]
    components["x3_errorline"] = plt.plot([],[],color=COLOUR_RECONSTRUCTED_AGE)[0]
    components["y3_errorline"] = plt.plot([],[],color=COLOUR_RECONSTRUCTED_AGE)[0]
    components["t_errorline"] = plt.plot([],[],color=COLOUR_RECONSTRUCTED_AGE, linewidth=2)[0]
    components["t_text"] = plt.text(12, 0.4,"Age")

    plt.text(3,0.55, "(all errors plotted at " + str(SIGMAS_OUTPUT_ERROR) + "σ)", fontsize=8)
    return components  

def _get_label_text(t, t_min, t_max):
    toMa = lambda t : int(t/(10**6))

    result = "Age = "
    result += str(toMa(t)) if t is not None else "???"
    result += " Ma"

    if t_min is None:
        t_min_error = None
    else:
        t_min_error = utils.round_to_sf(utils.convert_from_stddev_without_sigmas(toMa(t), toMa(t) - toMa(t_min), ERROR_TYPE_OUTPUT), OUTPUT_SIGNIFICANT_FIGURES)

    if t_max is None:
        t_max_error = None
    else:
        t_max_error = utils.round_to_sf(utils.convert_from_stddev_without_sigmas(toMa(t), toMa(t_max) - toMa(t), ERROR_TYPE_OUTPUT), OUTPUT_SIGNIFICANT_FIGURES)

    result += "\n- " + str(SIGMAS_OUTPUT_ERROR) + "σ = "
    result += str(t_min_error) if t_min_error is not None else "???"
    result += utils.error_symbol(ERROR_TYPE_OUTPUT)

    result += "\n+" + str(SIGMAS_OUTPUT_ERROR) + "σ = "
    result += str(t_max_error) if t_max_error is not None else "???"
    result += utils.error_symbol(ERROR_TYPE_OUTPUT)
    return result

def _update_plot(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206, mean, lower_bound, upper_bound):
    x1 = error.value(rim_u238pb206)
    y1 = error.value(rim_pb207pb206)
    x1_error = error.stddev(rim_u238pb206)*SIGMAS_OUTPUT_ERROR
    y1_error = error.stddev(rim_pb207pb206)*SIGMAS_OUTPUT_ERROR

    x2 = error.value(discordant_u238pb206)
    y2 = error.value(discordant_pb207pb206)
    x2_error = error.stddev(discordant_u238pb206)*SIGMAS_OUTPUT_ERROR
    y2_error = error.stddev(discordant_pb207pb206)*SIGMAS_OUTPUT_ERROR

    xdata = [x1,x2]
    ydata = [y1,y2]


    if mean is None:
        t_error_xs = []
        t_error_ys = []
        x3_error_xs = []
        x3_error_ys = []
        y3_error_xs = []
        y3_error_ys = []
        t_label_text = _get_label_text(None, None, None)
    else:
        (t, x3, y3) = mean
        xdata += [x3]
        ydata += [y3]

        x3_error_ys = [y3,y3]
        y3_error_xs = [x3,x3]


        if lower_bound is None or upper_bound is None:
            t_error_xs = []
            t_error_ys = []
            x3_error_xs = [None, None]
            y3_error_ys = [None, None]
            t_label_text = _get_label_text(t, None, None)
        else:
            t_min, x3_min, y3_min = lower_bound
            t_max, x3_max, y3_max = upper_bound

            x3_error_xs = [x3_min, x3_max]
            y3_error_ys = [y3_min, y3_max]
            ts = list(np.linspace(start=t_min, stop=t_max, num=20))
            t_error_xs = [calculations.u238pb206_from_age(t) for t in ts]
            t_error_ys = [calculations.pb207pb206_from_age(t) for t in ts]
            t_label_text = _get_label_text(t, t_min, t_max)

    components["x1_errorline"].set_xdata([x1-x1_error,x1+x1_error])
    components["x2_errorline"].set_xdata([x2-x2_error,x2+x2_error])
    components["x1_errorline"].set_ydata([y1,y1])
    components["x2_errorline"].set_ydata([y2,y2])
    components["y1_errorline"].set_xdata([x1,x1])
    components["y2_errorline"].set_xdata([x2,x2])
    components["y1_errorline"].set_ydata([y1-y1_error,y1+y1_error])
    components["y2_errorline"].set_ydata([y2-y2_error,y2+y2_error])
    components["x3_errorline"].set_xdata(x3_error_xs)
    components["x3_errorline"].set_ydata(x3_error_ys)
    components["y3_errorline"].set_xdata(y3_error_xs)
    components["y3_errorline"].set_ydata(y3_error_ys)
    components["t_errorline"].set_xdata(t_error_xs)
    components["t_errorline"].set_ydata(t_error_ys)
    components["t_text"].set_text(t_label_text)
    components["best_fit_line"].set_xdata(xdata)
    components["best_fit_line"].set_ydata(ydata)
    plt.draw()

def run():
    # Creating sliders
    slider_startx = 0.19
    slider_length = 0.7
    slider_height = 0.03
    plt.subplots_adjust(bottom=0.45, right=0.78)
    axcolor = 'lightgoldenrodyellow'
    rim_age_axis = plt.axes([slider_startx, 0.3, slider_length, slider_height], facecolor=axcolor)
    rim_age_error_axis = plt.axes([slider_startx, 0.25, slider_length, slider_height], facecolor=axcolor)
    point_x_axis = plt.axes([slider_startx, 0.2, slider_length, slider_height], facecolor=axcolor)
    point_x_error_axis = plt.axes([slider_startx, 0.15, slider_length, slider_height], facecolor=axcolor)
    point_y_axis = plt.axes([slider_startx, 0.1, slider_length, slider_height], facecolor=axcolor)
    point_y_error_axis = plt.axes([slider_startx, 0.05, slider_length, slider_height], facecolor=axcolor)

    rim_age_slider = Slider(
        rim_age_axis, 
        'Rim age (Ma)', 
        MIN_VALUE_RIM_AGE, 
        MAX_VALUE_RIM_AGE, 
        valinit=DEFAULT_VALUE_RIM_AGE
    )
    rim_age_error_slider = Slider(
        rim_age_error_axis, 
        '± ' + utils.ERROR_STR_RIM_AGE, 
        utils.ACTUAL_MIN_VALUE_RIM_AGE_ERROR, 
        utils.ACTUAL_MAX_VALUE_RIM_AGE_ERROR, 
        valinit=utils.ACTUAL_DEFAULT_VALUE_RIM_AGE_ERROR
    )
    point_x_slider = Slider(
        point_x_axis, 
        LABEL_U238Pb206, 
        MIN_VALUE_MIXED_POINT_U238Pb206, 
        MAX_VALUE_MIXED_POINT_U238Pb206, 
        valinit=DEFAULT_VALUE_MIXED_POINT_U238Pb206
    )
    point_x_error_slider = Slider(
        point_x_error_axis, 
        '± ' + utils.ERROR_STR_MIXED_POINT, 
        utils.ACTUAL_MIN_VALUE_MIXED_POINT_U238Pb206_ERROR,
        utils.ACTUAL_MAX_VALUE_MIXED_POINT_U238Pb206_ERROR, 
        valinit=utils.ACTUAL_DEFAULT_VALUE_MIXED_POINT_U238Pb206_ERROR
    )
    point_y_slider = Slider(
        point_y_axis, 
        LABEL_Pb207Pb206, 
        MIN_VALUE_MIXED_POINT_Pb207Pb206, 
        MAX_VALUE_MIXED_POINT_Pb207Pb206, 
        valinit=DEFAULT_VALUE_MIXED_POINT_Pb207Pb206
    )
    point_y_error_slider = Slider(
        point_y_error_axis, 
        '± ' + utils.ERROR_STR_MIXED_POINT, 
        utils.ACTUAL_MIN_VALUE_MIXED_POINT_Pb207Pb206_ERROR, 
        utils.ACTUAL_MAX_VALUE_MIXED_POINT_Pb207Pb206_ERROR, 
        valinit=utils.ACTUAL_DEFAULT_VALUE_MIXED_POINT_Pb207Pb206_ERROR
    )

    # Create error order buttons
    error_order_axis = plt.axes([0.8, 0.73, 0.19, 0.15], facecolor=axcolor)
    error_order_buttons = RadioButtons(error_order_axis, ('1st order', '2nd order', "MC estimate"), active=1)

    def update(e):
        order = error_order_buttons.value_selected
        if "1st" in order:
            error.set_order(1)
        elif "2nd" in order:
            error.set_order(2)
        else:
            error.set_order("mc")

        rim_age_error = utils.convert_to_stddev(rim_age_slider.val, rim_age_error_slider.val, ERROR_TYPE_RIM_AGE, SIGMAS_RIM_AGE_ERROR)
        discordant_u238pb206_error = utils.convert_to_stddev(point_x_slider.val, point_x_error_slider.val, ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)
        discordant_pb207pb206_error = utils.convert_to_stddev(point_y_slider.val, point_y_error_slider.val, ERROR_TYPE_MIXED_POINT, SIGMAS_MIXED_POINT_ERROR)

        rim_age = error.ufloat(rim_age_slider.val, rim_age_error)*(10**6)
        discordant_u238pb206 = error.ufloat(point_x_slider.val, discordant_u238pb206_error)
        discordant_pb207pb206 = error.ufloat(point_y_slider.val, discordant_pb207pb206_error)

        rim_u238pb206 = calculations.u238pb206_from_age(rim_age)
        rim_pb207pb206 = calculations.pb207pb206_from_age(rim_age)

        mean, lower_bound, upper_bound = calculations.reconstruct_age(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206)

        _update_plot(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206, mean, lower_bound, upper_bound)

    rim_age_slider.on_changed(update)
    rim_age_error_slider.on_changed(update)
    point_x_slider.on_changed(update)
    point_x_error_slider.on_changed(update)
    point_y_slider.on_changed(update)
    point_y_error_slider.on_changed(update)
    error_order_buttons.on_clicked(update)

    update(None)

    plt.show()


def plot_and_save(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206, mean, lower_bound, upper_bound, sample_name, output_path):
    _update_plot(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206, mean, lower_bound, upper_bound)
    plt.title(sample_name)
    plt.savefig(output_path)

components = _generate_basic_concordia_plot()
