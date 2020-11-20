from typing import Tuple, Optional, List

import matplotlib
#matplotlib.use('QT5Agg')
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QGroupBox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

from model.settings.calculation import CalculationSettings
from model.spot import Spot
from utils import config, string
import utils.calculations as calculations


class GraphPanel(QGroupBox):
    _default_x_lim = (-1, 18)
    _default_y_lim = (0, 0.6)

    def __init__(self):
        super().__init__("TW concordia plot")

        graph_widget = self.createGraph()
        graph_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(graph_widget)
        self.setLayout(layout)

    def _setup_concordia_plot(self, axis):
        axis.set_xlabel("${}^{238}U/{}^{206}Pb$")
        axis.set_ylabel("${}^{207}Pb/{}^{206}Pb$")

        max_age = 6000
        min_age = 1
        x_min = calculations.u238pb206_from_age(max_age * (10 ** 6))
        x_max = calculations.u238pb206_from_age(min_age * (10 ** 6))

        # Plot concordia curve
        xs = np.arange(x_min, x_max, 0.1)
        ys = [calculations.pb207pb206_from_u238pb206(x) for x in xs]
        axis.plot(xs, ys)

        # Plot concordia times
        ts2 = list(range(10, 100, 10)) + list(range(100, 500, 100)) + list(range(500, max_age + 1, 500))
        xs2 = [calculations.u238pb206_from_age(t * (10 ** 6)) for t in ts2]
        ys2 = [calculations.pb207pb206_from_age(t * (10 ** 6)) for t in ts2]
        axis.scatter(xs2, ys2)
        for i, txt in enumerate(ts2):
            axis.annotate(
                str(txt) + " ",
                (xs2[i], ys2[i]),
                horizontalalignment="right",
                verticalalignment="top",
                fontsize="small"
            )

    def createGraph(self):
        fig, self.axis = plt.subplots()
        plt.xlim(*self._default_x_lim)
        plt.ylim(*self._default_y_lim)
        plt.tight_layout(rect=[0.05, 0.08, 1, 0.95])
        self.axis.spines['top'].set_visible(False)
        self.axis.spines['right'].set_visible(False)

        self._setup_concordia_plot(self.axis)

        # plot
        self.canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        layout.addWidget(toolbar)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return widget

    def displayRows(self, rows, calculationSettings):
        self.axis.clear()
        self._setup_concordia_plot(self.axis)

        if len(rows) == 1:
            self._display_spot(rows[0], calculationSettings)
        elif rows:
            self._display_spots(rows, calculationSettings)

        self.canvas.draw()

    def _display_spot(self, spot: Optional[Spot], settings: CalculationSettings):

        if spot is None or spot.has_invalid_inputs() or not spot.has_outputs():
            self.axis.set_xlim(*self._default_x_lim)
            self.axis.set_ylim(*self._default_y_lim)

            if spot is not None and spot.has_invalid_inputs():
                label = "(imported data in row is invalid)"
            elif spot is not None and not spot.has_outputs():
                label = "(row not yet processed)"
            else:
                label = ""
            self.axis.text(0.95, 0.95, label, horizontalalignment='right', verticalalignment='top',
                                       transform=self.axis.transAxes)
            return

        x1 = spot.outputs.rim_u_pb_value
        y1 = spot.outputs.rim_pb_pb_value
        x1_error = spot.outputs.rim_u_pb_st_dev * settings.output_error_sigmas
        y1_error = spot.outputs.rim_pb_pb_st_dev * settings.output_error_sigmas

        x2 = spot.inputs.mixed_u_pb_value
        y2 = spot.inputs.mixed_pb_pb_value
        x2_error = spot.inputs.mixed_u_pb_st_dev * settings.output_error_sigmas
        y2_error = spot.inputs.mixed_pb_pb_st_dev * settings.output_error_sigmas

        # Data
        best_fit_line_xs = [x1, x2]
        best_fit_line_ys = [y1, y2]

        reconstructed_age = spot.outputs.reconstructed_age

        if reconstructed_age is None:
            x3s = []
            y3s = []
            t_error_xs = []
            t_error_ys = []
            x3_errors = []
            y3_errors = []
            t3_fmt = 'none'
            x_lim = self._default_x_lim
            y_start = min(y1 - y1_error, y2 - y2_error)
            y_end = max(y1 + y1_error, y2 + y2_error)
            _, y_lim = self._calculate_margin(x2 - x2_error, x1 + x1_error, y_start, y_end)
            label_text = "(no intercept with concordia curve found)"
            colour = config.INVALID_CALCULATION_COLOUR
        else:
            t, x3, y3 = reconstructed_age.get_values()
            t_min, x3_min, y3_min = reconstructed_age.get_min_values()
            t_max, x3_max, y3_max = reconstructed_age.get_max_values()

            best_fit_line_xs += [x3]
            best_fit_line_ys += [y3]

            label_text = "all errors at " + string.get_error_sigmas_str(settings.output_error_sigmas)
            if not t_min:
                t_min = t
                label_text += "\n (no lower error bar available for reconstructed age)"
            if not t_max:
                t_max = t
                label_text += "\n (no upper error bar available for reconstructed age)"
            t3_fmt = 'none' if reconstructed_age.valid else "^"

            if not x3_min:
                x3_min = x3
            if not x3_max:
                x3_max = x3
            if not y3_min:
                y3_min = y3
            if not y3_max:
                y3_max = y3

            x3s = [x3]
            y3s = [y3]
            x3_errors = [[x3 - x3_min], [x3_max - x3]]
            y3_errors = [[y3 - y3_min], [y3_max - y3]]

            ts = list(np.linspace(start=t_min, stop=t_max, num=20))
            t_error_xs = [calculations.u238pb206_from_age(t) for t in ts]
            t_error_ys = [calculations.pb207pb206_from_age(t) for t in ts]

            x_lim, y_lim = self._calculate_margin(x3_min, x1 + x1_error, y1 - y1_error, y3_max)

            if not reconstructed_age.valid:
                colour = config.INVALID_CALCULATION_COLOUR
            elif spot.outputs.rejected:
                colour = config.REJECTED_CALCULATION_COLOUR
            else:
                colour = config.VALID_CALCULATION_COLOUR

        self.axis.set_xlim(*x_lim)
        self.axis.set_ylim(*y_lim)

        # Best fit line
        self.axis.plot(best_fit_line_xs, best_fit_line_ys, linestyle='--', color=colour)
        # Rim points
        self.axis.errorbar([x1], [y1], xerr=[x1_error], yerr=[y1_error], fmt='none', color=colour)
        # Discordant points
        self.axis.errorbar([x2], [y2], xerr=[x2_error], yerr=[y2_error], fmt='none', color=colour)
        # Reconstructed age error line
        self.axis.plot(t_error_xs, t_error_ys, color=colour, linewidth=2)
        # Reconstructed age xy points
        self.axis.errorbar(x3s, y3s, xerr=x3_errors, yerr=y3_errors, fmt=t3_fmt, color=colour)
        # Text
        self.axis.text(0.95, 0.95, label_text, horizontalalignment='right', verticalalignment='top',
                                   transform=self.axis.transAxes)

    def _display_spots(self, spots: List[Spot], settings: CalculationSettings):
        valid_xs = []
        valid_ys = []
        valid_xs_error_min = []
        valid_xs_error_max = []
        valid_ys_error_min = []
        valid_ys_error_max = []

        invalid_xs = []
        invalid_ys = []
        invalid_xs_error_min = []
        invalid_xs_error_max = []
        invalid_ys_error_min = []
        invalid_ys_error_max = []

        rejected_xs = []
        rejected_ys = []
        rejected_xs_error_min = []
        rejected_xs_error_max = []
        rejected_ys_error_min = []
        rejected_ys_error_max = []

        x_max, x_min = self._default_x_lim
        y_max, y_min = self._default_y_lim

        any_rows = False
        any_invalid_rows = False
        for spot in spots:
            if spot.has_invalid_inputs() or not spot.has_outputs() or spot.outputs.reconstructed_age is None:
                continue

            any_rows = True
            reconstructed_age = spot.outputs.reconstructed_age
            t, x3, y3 = reconstructed_age.get_values()
            t_min, x3_min, y3_min = reconstructed_age.get_min_values()
            t_max, x3_max, y3_max = reconstructed_age.get_max_values()

            if not x3_min:
                x3_min = x3
            if not x3_max:
                x3_max = x3
            if not y3_min:
                y3_min = y3
            if not y3_max:
                y3_max = y3

            if not reconstructed_age.valid:
                any_invalid_rows = True
                xs = invalid_xs
                ys = invalid_ys
                xs_error_min = invalid_xs_error_min
                xs_error_max = invalid_xs_error_max
                ys_error_min = invalid_ys_error_min
                ys_error_max = invalid_ys_error_max
            elif spot.outputs.rejected:
                xs = rejected_xs
                ys = rejected_ys
                xs_error_min = rejected_xs_error_min
                xs_error_max = rejected_xs_error_max
                ys_error_min = rejected_ys_error_min
                ys_error_max = rejected_ys_error_max
            else:
                xs = valid_xs
                ys = valid_ys
                xs_error_min = valid_xs_error_min
                xs_error_max = valid_xs_error_max
                ys_error_min = valid_ys_error_min
                ys_error_max = valid_ys_error_max

            xs += [x3]
            ys += [y3]

            x_min = min(x_min, x3_min)
            x_max = max(x_max, x3_max)
            y_min = min(y_min, y3_min)
            y_max = max(y_max, y3_max)

            xs_error_min += [x3 - x3_min]
            xs_error_max += [x3_max - x3]
            ys_error_min += [y3 - y3_min]
            ys_error_max += [y3_max - y3]

        valid_xs_error = valid_xs_error_min, valid_xs_error_max
        valid_ys_error = valid_ys_error_min, valid_ys_error_max
        invalid_xs_error = invalid_xs_error_min, invalid_xs_error_max
        invalid_ys_error = invalid_ys_error_min, invalid_ys_error_max
        rejected_xs_error = rejected_xs_error_min, rejected_xs_error_max
        rejected_ys_error = rejected_ys_error_min, rejected_ys_error_max

        if any_rows:
            x_lim, y_lim = self._calculate_margin(x_min, x_max, y_min, y_max)
        else:
            x_lim, y_lim = self._default_x_lim, self._default_y_lim

        if all(row.has_invalid_inputs() for row in spots):
            label_text = "(imported data in rows is invalid)"
        elif not any(row.has_outputs() for row in spots):
            label_text = "(rows not yet processed)"
        else:
            label_text = "all errors at " + string.get_error_sigmas_str(settings.output_error_sigmas)

        if any_invalid_rows:
            label_text += "\n (some error bars unavailable)"

        self.axis.errorbar(
            valid_xs, valid_ys,
            xerr=valid_xs_error, yerr=valid_ys_error,
            fmt='none',
            color=config.VALID_CALCULATION_COLOUR
        )
        self.axis.errorbar(
            invalid_xs, invalid_ys,
            xerr=invalid_xs_error, yerr=invalid_ys_error,
            fmt='^',
            color=config.INVALID_CALCULATION_COLOUR
        )
        self.axis.errorbar(
            rejected_xs, rejected_ys,
            xerr=rejected_xs_error, yerr=rejected_ys_error,
            fmt='^',
            color=config.REJECTED_CALCULATION_COLOUR
        )

        self.axis.set_xlim(*x_lim)
        self.axis.set_ylim(*y_lim)
        self.axis.text(
            0.95, 0.95,
            label_text,
            horizontalalignment='right',
            verticalalignment='top',
            transform=self.axis.transAxes
        )

    @staticmethod
    def _calculate_margin(x_min, x_max, y_min, y_max) -> Tuple[float, float]:
        x_margin = x_max * 0.1
        y_margin = y_max * 0.1

        x_lim = (max(0, x_min - x_margin), x_max + x_margin)
        y_lim = (max(0, y_min - y_margin), y_max + y_margin)

        return x_lim, y_lim
