from PyQt5.QtWidgets import *

from tabs.abstract.abstractGraphPanel import AbstractGraphPanel

import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

import config
import model.calculations as calculations


class UnmixGraphPanel(AbstractGraphPanel):
    _default_xlim = (-1, 18)
    _default_ylim = (0, 0.6)

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QFormLayout()
        layout.addRow(self.createGraph())
        self.setLayout(layout)

    def createGraph(self):
        widget = QWidget()

        fig, self.axis = plt.subplots()
        plt.xlim(*self._default_xlim)
        plt.ylim(*self._default_ylim)
        plt.tight_layout(rect=[0.05, 0.08, 1, 0.95])

        self._setupConcordiaPlot(self.axis)

        # plot
        self.canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        layout.addWidget(toolbar)
        widget.setLayout(layout)
        return widget

    def displayRows(self, rows, calculationSettings):
        self.axis.clear()
        self._setupConcordiaPlot(self.axis)

        if len(rows) == 1:
            self._displayRow(rows[0], calculationSettings)
        elif rows:
            self._displayRows(rows, calculationSettings)

        self.canvas.draw()

    def _displayRow(self, row, calculationSettings):

        if row is None or not row.validImports or not row.processed:
            self.axis.set_xlim(*self._default_xlim)
            self.axis.set_ylim(*self._default_ylim)

            label = ""
            if row is not None and not row.validImports and row.processed:
                label = "*imported data is invalid"
            elif row is not None and row.validImports and not row.processed:
                label = "*data not yet processed"
            else:
                label = ""
            self.axis.text(0.95, 0.95, label, horizontalalignment='right', verticalalignment='top', transform=self.axis.transAxes)
            return

        x1 = row.rimUPbValue
        y1 = row.rimPbPbValue
        x1_error = row.rimUPbStDev * calculationSettings.outputErrorSigmas
        y1_error = row.rimPbPbStDev * calculationSettings.outputErrorSigmas

        x2 = row.mixedUPbValue
        y2 = row.mixedPbPbValue
        x2_error = row.mixedUPbStDev * calculationSettings.outputErrorSigmas
        y2_error = row.mixedPbPbStDev * calculationSettings.outputErrorSigmas

        # Data
        best_fit_line_xs = [x1, x2]
        best_fit_line_ys = [y1, y2]

        reconstructedAge = row.reconstructedAgeObj

        if not reconstructedAge.hasValue():
            t_xs = []
            t_ys = []
            t_error_xs = []
            t_error_ys = []
            x3_error_xs = []
            y3_error_ys = []
            # t_label_text = _get_label_text(None, None, None)
            xlim = self._default_xlim
            ylim = self._default_ylim
        else:
            (t, x3, y3) = reconstructedAge.values
            best_fit_line_xs += [x3]
            best_fit_line_ys += [y3]

            t_xs = [x3]
            t_ys = [y3]

            if not reconstructedAge.hasMinValue() or not reconstructedAge.hasMaxValue():
                t_error_xs = []
                t_error_ys = []
                x3_error_xs = [[0], [0]]
                y3_error_ys = [[0], [0]]
                xlim, ylim = self._calculateMargin(x3, x1 + x1_error, y1 - y1_error, y3)
                label_text = "*no error bars available"
                t3_fmt = "^"
            else:
                t_min, x3_min, y3_min = reconstructedAge.minValues
                t_max, x3_max, y3_max = reconstructedAge.maxValues

                x3_error_xs = [[x3-x3_min], [x3_max-x3]]
                y3_error_ys = [[y3-y3_min], [y3_max-y3]]
                ts = list(np.linspace(start=t_min, stop=t_max, num=20))
                t_error_xs = [calculations.u238pb206_from_age(t) for t in ts]
                t_error_ys = [calculations.pb207pb206_from_age(t) for t in ts]

                xlim, ylim = self._calculateMargin(x3_min, x1 + x1_error, y1 - y1_error, y3_max)
                t3_fmt = 'none'
                label_text = ""
                # t_label_text = _get_label_text(t, t_min, t_max)

        self.axis.set_xlim(*xlim)
        self.axis.set_ylim(*ylim)

        # Best fit line
        self.axis.plot(best_fit_line_xs, best_fit_line_ys, linestyle='--')
        # Rim points
        self.axis.errorbar([x1], [y1], xerr=[x1_error], yerr=[y1_error], fmt='none', color=config.COLOUR_RIM_AGE)
        # Discordant points
        self.axis.errorbar([x2], [y2], xerr=[x2_error], yerr=[y2_error], fmt='none', color=config.COLOUR_MIXED_POINT)
        # Reconstructed age error line
        self.axis.plot(t_error_xs, t_error_ys, color=config.COLOUR_RECONSTRUCTED_AGE, linewidth=2)[0]
        # Reconstructed age xy points
        self.axis.errorbar(t_xs, t_ys, xerr=x3_error_xs, yerr=y3_error_ys, fmt=t3_fmt, color=config.COLOUR_RECONSTRUCTED_AGE)
        # Text
        self.axis.text(0.95, 0.95, label_text, horizontalalignment='right', verticalalignment='top', transform=self.axis.transAxes)
        #plt.text(12, 0.4, t_label_text)



    def _displayRows(self, rows, calculationSettings):
        xs = []
        ys = []
        xs_error_min = []
        xs_error_max = []
        ys_error_min = []
        ys_error_max = []
        bad_xs = []
        bad_ys = []

        xmax, xmin = self._default_xlim
        ymax, ymin = self._default_ylim

        for row in rows:
            if not row.validImports or not row.processed or row.reconstructedAgeObj is None:
                continue

            reconstructedAge = row.reconstructedAgeObj
            (t, x3, y3) = reconstructedAge.values

            if not reconstructedAge.hasMinValue() or not reconstructedAge.hasMaxValue():
                bad_xs += [x3]
                bad_ys += [y3]

                xmin = min(xmin, x3)
                xmax = max(xmax, x3)
                ymin = min(ymin, y3)
                ymax = max(ymax, y3)
            else:
                t_min, x3_min, y3_min = reconstructedAge.minValues
                t_max, x3_max, y3_max = reconstructedAge.maxValues

                xs += [x3]
                ys += [y3]

                xs_error_min += [x3 - x3_min]
                xs_error_max += [x3_max - x3]
                ys_error_min += [y3 - y3_min]
                ys_error_max += [y3_max - y3]

                xmin = min(xmin, x3_min)
                xmax = max(xmax, x3_max)
                ymin = min(ymin, y3_min)
                ymax = max(ymax, y3_max)

        xs_error = xs_error_min, xs_error_max
        ys_error = ys_error_min, ys_error_max

        if (xmax, xmin) == self._default_xlim:
            xmin, xmax = self._default_xlim
        if (ymax, ymin) == self._default_ylim:
            ymin, ymax = self._default_ylim

        xlim, ylim = self._calculateMargin(xmin, xmax, ymin, ymax)

        self.axis.errorbar(xs, ys, xerr=xs_error, yerr=ys_error, fmt='none', color=config.COLOUR_RECONSTRUCTED_AGE)
        self.axis.errorbar(bad_xs, bad_ys, fmt='^', color=config.COLOUR_RECONSTRUCTED_AGE)

        self.axis.set_xlim(*xlim)
        self.axis.set_ylim(*ylim)

    def _calculateMargin(self, xmin, xmax, ymin, ymax):
        xmargin = xmax * 0.1
        ymargin = ymax * 0.1

        xlim = (max(0, xmin - xmargin), xmax + xmargin)
        ylim = (max(0, ymin - ymargin), ymax + ymargin)

        return xlim, ylim


    def onProcessingProgress(self, i, row):
        pass

    def updatePlot(self):
        print("Update!")
