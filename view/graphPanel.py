from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

import config
import utils

import model.calculations as calculations

class GraphPanel(QGroupBox):

    _default_xlim = (-1,18)
    _default_ylim = (0, 0.6)

    def __init__(self, *args, **kwargs):
        super(GraphPanel, self).__init__("Interactive", *args, **kwargs)
        self.initUI()

    def initUI(self):
        layout = QFormLayout()
        layout.addRow(self.createGraph())
        self.setLayout(layout)

    def createGraph(self):
        widget = QWidget()

        fig, axis = plt.subplots()
        plt.xlim(*self._default_xlim)
        plt.ylim(*self._default_ylim)
        plt.xlabel("${}^{238}U/{}^{206}Pb$")
        plt.ylabel("${}^{207}Pb/{}^{206}Pb$")

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

        # Create the error lines
        components = {}
        components["best_fit_line"] = plt.plot([],[],[],[],linestyle='--')[0]
        components["x1_errorline"] = plt.plot([],[],color=config.COLOUR_RIM_AGE)[0]
        components["y1_errorline"] = plt.plot([],[],color=config.COLOUR_RIM_AGE)[0]
        components["x2_errorline"] = plt.plot([],[],color=config.COLOUR_MIXED_POINT)[0]
        components["y2_errorline"] = plt.plot([],[],color=config.COLOUR_MIXED_POINT)[0]
        components["x3_errorline"] = plt.plot([],[],color=config.COLOUR_RECONSTRUCTED_AGE)[0]
        components["y3_errorline"] = plt.plot([],[],color=config.COLOUR_RECONSTRUCTED_AGE)[0]
        components["t_errorline"] = plt.plot([],[],color=config.COLOUR_RECONSTRUCTED_AGE, linewidth=2)[0]
        components["t_text"] = plt.text(12, 0.4,"")
        self.components = components

        # plot
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()  
        layout.setContentsMargins(0, 0, 0, 0)      
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        widget.setLayout(layout)
        return widget

    def displayRow(self, row, settings):
        if not row.validInput:
            self.clear()
            return

        x1 = row.rimUPbValue
        y1 = row.rimPbPbValue
        x1_error = row.rimUPbStDev*settings.outputErrorSigmas
        y1_error = row.rimPbPbStDev*settings.outputErrorSigmas

        x2 = row.mixedUPbValue
        y2 = row.mixedPbPbValue
        x2_error = row.mixedUPbStDev*settings.outputErrorSigmas
        y2_error = row.mixedPbPbStDev*settings.outputErrorSigmas

        xdata = [x1,x2]
        ydata = [y1,y2]

        if row.reconstructedValues is None:
            t_error_xs = []
            t_error_ys = []
            x3_error_xs = []
            x3_error_ys = []
            y3_error_xs = []
            y3_error_ys = []
            t_label_text = _get_label_text(None, None, None)
            xlim = self._default_xlim
            ylim = self._default_ylim
        else:
            (t, x3, y3) = row.reconstructedValues
            xdata += [x3]
            ydata += [y3]

            x3_error_ys = [y3,y3]
            y3_error_xs = [x3,x3]

            if row.minReconstructedValues is None or row.maxReconstructedValues is None:
                t_error_xs = []
                t_error_ys = []
                x3_error_xs = [None, None]
                y3_error_ys = [None, None]
                xlim = self._default_xlim
                ylim = self._default_ylim
                #t_label_text = _get_label_text(t, None, None)
            else:
                t_min, x3_min, y3_min = row.minReconstructedValues
                t_max, x3_max, y3_max = row.maxReconstructedValues

                x3_error_xs = [x3_min, x3_max]
                y3_error_ys = [y3_min, y3_max]
                ts = list(np.linspace(start=t_min, stop=t_max, num=20))
                t_error_xs = [calculations.u238pb206_from_age(t) for t in ts]
                t_error_ys = [calculations.pb207pb206_from_age(t) for t in ts]

                xmargin = (x1+x1_error)*0.1
                ymargin = y3_max*0.1

                xlim = (max(0,x3_max - xmargin), x1+x1_error + xmargin)
                ylim = (max(0, y1-y1_error - ymargin), y3_max + ymargin)
                #t_label_text = _get_label_text(t, t_min, t_max)


        plt.xlim(*xlim)
        plt.ylim(*ylim)
        self.components["best_fit_line"].set_xdata(xdata)
        self.components["best_fit_line"].set_ydata(ydata)
        self.components["x1_errorline"].set_xdata([x1-x1_error,x1+x1_error])
        self.components["x2_errorline"].set_xdata([x2-x2_error,x2+x2_error])
        self.components["x1_errorline"].set_ydata([y1,y1])
        self.components["x2_errorline"].set_ydata([y2,y2])
        self.components["y1_errorline"].set_xdata([x1,x1])
        self.components["y2_errorline"].set_xdata([x2,x2])
        self.components["y1_errorline"].set_ydata([y1-y1_error,y1+y1_error])
        self.components["y2_errorline"].set_ydata([y2-y2_error,y2+y2_error])
        self.components["x3_errorline"].set_xdata(x3_error_xs)
        self.components["x3_errorline"].set_ydata(x3_error_ys)
        self.components["y3_errorline"].set_xdata(y3_error_xs)
        self.components["y3_errorline"].set_ydata(y3_error_ys)
        self.components["t_errorline"].set_xdata(t_error_xs)
        self.components["t_errorline"].set_ydata(t_error_ys)
        #self.components["t_text"].set_text(t_label_text)
        self.canvas.draw()

    def clear(self):
        self.components["best_fit_line"].set_xdata([])
        self.components["best_fit_line"].set_ydata([])
        self.components["x1_errorline"].set_xdata([])
        self.components["x2_errorline"].set_xdata([])
        self.components["x1_errorline"].set_ydata([])
        self.components["x2_errorline"].set_ydata([])
        self.components["y1_errorline"].set_xdata([])
        self.components["y2_errorline"].set_xdata([])
        self.components["y1_errorline"].set_ydata([])
        self.components["y2_errorline"].set_ydata([])
        self.components["x3_errorline"].set_xdata([])
        self.components["x3_errorline"].set_ydata([])
        self.components["y3_errorline"].set_xdata([])
        self.components["y3_errorline"].set_ydata([])
        self.components["t_errorline"].set_xdata([])
        self.components["t_errorline"].set_ydata([])
        self.canvas.draw()

    def updatePlot(self):
        print("Update!")