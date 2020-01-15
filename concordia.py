import argparse
import csv
import math
from scipy.optimize import root_scalar
from uncertainties import ufloat
import uncertainties.umath as umath

input_file_help = """The path to the input csv file. The file should be in the format:
    \nsampleID\nspotID\nU238/Pb206\nU238/Pb206 error"""
output_file_help = "The path to store the output csv file."

SAMPLE_ID = "Sample ID"
SPOT_ID = "Spot ID"
U238Pb206 = "238U/206Pb"
U238Pb206_ERROR = U238Pb206 + " error (1σ)"
Pb207Pb206 = "207Pb/206Pb"
Pb207Pb206_ERROR = Pb207Pb206 + " error (1σ)"
LOWER_INTERCEPT_AGE = "Lower intercept age (Ma)"
LOWER_INTERCEPT_AGE_ERROR = "Lower intercept age (MA)"
FINAL_AGE = "age (Ma)"
FINAL_AGE_ERROR = "age error (Ma)"

SHARED_FIELDS = [
    SAMPLE_ID,
    SPOT_ID
]

INPUT_FIELDS = SHARED_FIELDS + [
    U238Pb206,
    U238Pb206_ERROR,
    Pb207Pb206,
    Pb207Pb206_ERROR,
    LOWER_INTERCEPT_AGE,
    LOWER_INTERCEPT_AGE_ERROR
]

OUTPUT_FIELDS = SHARED_FIELDS + [
    FINAL_AGE,
    FINAL_AGE_ERROR
]

U238_DECAY_CONSTANT = 1.54*(10**-10)
U235_DECAY_CONSTANT = 9.72*(10**-10)
U238U235_RATIO = 137.818

def plot():
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider
    from matplotlib.patches import Ellipse

    fig,ax = plt.subplots(1)

    # Plot concordia curve
    xs = np.arange(1.5,18,0.1)
    ys = [calculate_pb207pb206_from_u238pb206(x) for x in xs]
    plt.plot(xs,ys)

    # Plot concordia times
    ts2 = list(range(500, 3500, 500))
    xs2 = [calculate_u238pb206_from_age(t*(10**6)) for t in ts2]
    ys2 = [calculate_pb207pb206_from_age(t*(10**6)) for t in ts2]
    plt.scatter(xs2,ys2)
    for i, txt in enumerate(ts2):
        plt.annotate(txt, (xs2[i], ys2[i]))
    print(ts2,xs2,ys2)

    # Tidying up
    plt.xlim(1.5,18)
    plt.xlabel(U238Pb206)
    plt.ylabel(Pb207Pb206)

    # Plotting data
    line = plt.plot([],[],[],[])[0]
    x1_errorline = plt.plot([],[],color='r')[0]
    x2_errorline = plt.plot([],[],color='r')[0]
    y1_errorline = plt.plot([],[],color='r')[0]
    y2_errorline = plt.plot([],[],color='r')[0]
    y3_errorline = plt.plot([],[],color='r')[0]
    t_errorline = plt.plot([],[],color='r', linewidth=2)[0]
    t_text = plt.text(10, 0.22,"Age")

    # Creating sliders
    slider_startx = 0.27
    slider_length = 0.65
    slider_height = 0.03

    plt.subplots_adjust(bottom=0.45)
    axcolor = 'lightgoldenrodyellow'
    rim_age_axis = plt.axes([slider_startx, 0.3, slider_length, slider_height], facecolor=axcolor)
    rim_age_error_axis = plt.axes([slider_startx, 0.25, slider_length, slider_height], facecolor=axcolor)
    point_x_axis = plt.axes([slider_startx, 0.2, slider_length, slider_height], facecolor=axcolor)
    point_x_error_axis = plt.axes([slider_startx, 0.15, slider_length, slider_height], facecolor=axcolor)
    point_y_axis = plt.axes([slider_startx, 0.1, slider_length, slider_height], facecolor=axcolor)
    point_y_error_axis = plt.axes([slider_startx, 0.05, slider_length, slider_height], facecolor=axcolor)
    #axamp = plt.axes([0.1, 0.1, 0.75, 0.03], facecolor=axcolor)
    rim_age_slider = Slider(rim_age_axis, 'Rim age (Ma)', 300.0, 1000.0, valinit=500)
    rim_age_error_slider = Slider(rim_age_error_axis, 'Rim age error (Ma)', 0.0, 50.0, valinit=25)
    point_x_slider = Slider(point_x_axis, U238Pb206, 4, 12, valinit=7)
    point_x_error_slider = Slider(point_x_error_axis, U238Pb206_ERROR, 0, 1, valinit=0.5)
    point_y_slider = Slider(point_y_axis, Pb207Pb206, 0.08, 0.18, valinit=0.1)
    point_y_error_slider = Slider(point_y_error_axis, Pb207Pb206_ERROR, 0.0, 0.02, valinit=0.01)
    #famp = Slider(axamp, 'Amp', 0.1, 10.0, valinit=5)

    def update(e):
        rim_age = ufloat(rim_age_slider.val*(10**6), rim_age_error_slider.val*(10**6), "rim_age")
        rim_u238pb206 = calculate_u238pb206_from_age(rim_age)
        rim_pb207pb206 = calculate_pb207pb206_from_age(rim_age)

        discordant_u238pb206 = ufloat(point_x_slider.val, point_x_error_slider.val)
        discordant_pb207pb206 = ufloat(point_y_slider.val, point_y_error_slider.val)
        
        x1 = rim_u238pb206.nominal_value
        y1 = rim_pb207pb206.nominal_value
        x1_error = rim_u238pb206.std_dev
        y1_error = rim_pb207pb206.std_dev

        x2 = discordant_u238pb206.nominal_value
        y2 = discordant_pb207pb206.nominal_value
        x2_error = discordant_u238pb206.std_dev
        y2_error = discordant_pb207pb206.std_dev

        (t, t_min, t_max, x3, y3, y3_error) = create_age_estimation_function(rim_u238pb206, rim_pb207pb206, discordant_u238pb206, discordant_pb207pb206)

        x3 = calculate_u238pb206_from_age(t)
        y3 = calculate_pb207pb206_from_age(t)

        xdata = [x1,x2,x3]
        ydata = [y1,y2,y3]
        line.set_xdata(xdata)
        line.set_ydata(ydata)
        x1_errorline.set_xdata([x1-x1_error,x1+x1_error])
        x2_errorline.set_xdata([x2-x2_error,x2+x2_error])
        x1_errorline.set_ydata([y1,y1])
        x2_errorline.set_ydata([y2,y2])
        y1_errorline.set_xdata([x1,x1])
        y2_errorline.set_xdata([x2,x2])
        y1_errorline.set_ydata([y1-y1_error,y1+y1_error])
        y2_errorline.set_ydata([y2-y2_error,y2+y2_error])

        ts = list(np.linspace(start=t_min, stop=t_max, num=20))
        t_errorline.set_xdata([calculate_u238pb206_from_age(t) for t in ts])
        t_errorline.set_ydata([calculate_pb207pb206_from_age(t) for t in ts])

        toMa = lambda t : str(int(t/(10**6)))

        t_text.set_text("Age:     " + toMa(t) + "Ma\nRange: [" + toMa(t_min) + ", " + toMa(t_max) + "] Ma")

        y3_errorline.set_xdata([x3,x3])
        y3_errorline.set_ydata([y3-y3_error,y3+y3_error])

    rim_age_slider.on_changed(update)
    rim_age_error_slider.on_changed(update)
    point_x_slider.on_changed(update)
    point_x_error_slider.on_changed(update)
    point_y_slider.on_changed(update)
    point_y_error_slider.on_changed(update)

    update(None)

    plt.show()

def read_input(input_file):
    with open(input_file, newline='') as csvfile:
        raw_rows = csv.reader(csvfile, delimiter=' ', quotechar='|')
        rows = []
        for raw_row in raw_rows:
            rows.append({INPUT_FIELDS[i]:raw_row[i] for i in len(raw_row)})
    return rows

def write_output(output_file, output_rows):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [SAMPLE_ID, SPOT_ID, AGE, AGE_ERROR]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

def perform_calculations(rows):
    for row in rows:
        (lower_intercept_x, lower_intercept_x_error) = calculate_ratio_from_age(U238_DECAY_CONSTANT)
        (lower_intercept_y, lower_intercept_y_error) = None

        func = create_age_estimation_function(
            r[U238Pb206], r[U238Pb206_ERROR],
            r[Pb207Pb206], r[Pb207Pb206_ERROR],
            lower_intercept_x, lower_intercept_x_error,
            lower_intercept_y, lower_intercept_y_error
        )

        (age, age_error) = func.apply()

def calculate_age_from_u238pb206(u238pb206):
    return umath.log(1/u238pb206 + 1)/U238_DECAY_CONSTANT

def calculate_pb206u238_from_age(age):
    return umath.exp(U238_DECAY_CONSTANT * age) - 1

def calculate_u238pb206_from_age(age):
    return 1/calculate_pb206u238_from_age(age)

def calculate_pb207u235_from_age(age):
    return umath.exp(U235_DECAY_CONSTANT * age) - 1

def calculate_pb207pb206_from_age(age):
    pb207u235 = calculate_pb207u235_from_age(age)
    u238pb206 = calculate_u238pb206_from_age(age)
    return pb207u235*(1/U238U235_RATIO)*u238pb206

def calculate_pb207pb206_from_u238pb206(u238pb206):
    age = calculate_age_from_u238pb206(u238pb206)
    return calculate_pb207pb206_from_age(age)

def create_age_estimation_function(x1, y1, x2, y2):
    m = (y2 - y1)/(x2 - x1)
    c = y1 - m*x1

    root_min = calculate_age_from_u238pb206(min(x1.nominal_value,x2.nominal_value))
    root_max = 5*(10**9)

    root_range = (root_min, root_max)
    def minimisation_func(sign):
        def func(t):
            curve_pb207pb206 = calculate_pb207pb206_from_age(t)
            line_pb207pb206 = m*calculate_u238pb206_from_age(t) + c
            return curve_pb207pb206 - (line_pb207pb206.nominal_value + sign*line_pb207pb206.std_dev)
        return func

    main_solution = root_scalar(minimisation_func(0), bracket=root_range)
    min_solution = root_scalar(minimisation_func(-1), bracket=root_range)
    max_solution = root_scalar(minimisation_func(1), bracket=root_range)

    t = main_solution.root
    t_min = min_solution.root
    t_max = max_solution.root

    x = calculate_u238pb206_from_age(t)
    y = m*x+c
    print(y - y.std_dev, y + y.std_dev)

    return (t, t_min, t_max, x, y.nominal_value, y.std_dev)

"""
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help=input_file_help)
parser.add_argument("output_file", help=output_file_help)
args = parser.parse_args()

rows = read_input(args.input_file)
perform_calculations(rows)
write_output(rows)
"""


plot()

