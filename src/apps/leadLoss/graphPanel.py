from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from apps.abstract.graphPanel import AbstractGraphPanel

import matplotlib

from apps.leadLoss.model import Column

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import utils.calculations as calculations


class LeadLossGraphPanel(AbstractGraphPanel):
    _default_xlim = (-1, 18)
    _default_ylim = (0, 0.6)

    _age_xlim = (0, 5000)
    _statistic_ymax = 1.1

    _barResolution = 100
    _barMax = 5000
    _barMin = 0
    _bars = int((_barMax - _barMin) / _barResolution)

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller

        self.mouseOnStatisticsAxes = False

    def createGraph(self):
        widget = QWidget()
        fig = plt.figure()
        self.concordiaAxis = plt.subplot(221)
        self.statisticAxis = plt.subplot(222)
        self.concordantAxis = plt.subplot(223)
        self.discordantAxis = plt.subplot(224)

        plt.subplots_adjust(hspace = 0.9, wspace=0.4)

        # plot
        self.canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        layout.addWidget(toolbar)
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        widget.setLayout(layout)

        self.cid = fig.canvas.mpl_connect('motion_notify_event', self.onHover)
        self.cid2 = fig.canvas.mpl_connect('axes_enter_event', self.onMouseEnterAxes)
        self.cid3 = fig.canvas.mpl_connect('axes_leave_event', self.onMouseExitAxes)

        self.plotConcordia()
        self.plotConcordantHistogram([])
        self.plotDiscordantHistogram([])
        self.plotStatistics({})
        return widget

    def plotConcordia(self):
        self.concordiaAxis.set_xlim(*self._default_xlim)
        self.concordiaAxis.set_ylim(*self._default_ylim)
        self._setupConcordiaPlot(self.concordiaAxis)
        self.concordiaAxis.userAge = self.concordiaAxis.scatter([],[])
        self.concordiaAxis.set_title("TW concordia plot")

        self.concordiaAxis.chosenAgePoint = self.concordiaAxis.plot([], [], marker='o')[0]
        self.concordiaAxis.concordantDataPoints = self.concordiaAxis.plot([],[],label='toto',marker='o',ls='')[0]
        self.concordiaAxis.discordantDataPoints = self.concordiaAxis.plot([],[],label='toto',marker='o',ls='')[0]

    def plotDataPointsOnConcordiaAxis(self, rows):
        cxs = []
        cys = []
        dxs = []
        dys = []
        for row in rows:
            (cxs if row.concordant else dxs).append(row.importedCellsByCol[Column.U_PB].value)
            (cys if row.concordant else dys).append(row.importedCellsByCol[Column.PB_PB].value)

        self.concordiaAxis.concordantDataPoints.set_data(cxs,cys)
        self.concordiaAxis.discordantDataPoints.set_data(dxs,dys)

    def plotConcordantHistogram(self, values):
        scaledValues = [v/(10**6) for v in values]
        if values:
            weights = [1/len(values)]*len(values)
        else:
            weights = []

        self.concordantAxis.clear()
        self.concordantAxis.set_title("Concordant distribution")
        self.concordantAxis.set_xlabel("Age (Ma)")
        self.concordantAxis.set_xlim(*self._age_xlim)
        self.concordantAxis.set_ylim(0, 1.0)
        self.concordantAxis.hist(scaledValues, bins=self._bars, cumulative=True, weights=weights, range=(self._barMin, self._barMax))
        self.canvas.draw()

    def plotDiscordantHistogram(self, values):
        scaledValues = [v/(10**6) for v in values]
        if values:
            weights = [1/len(values)]*len(values)
        else:
            weights = []

        self.discordantAxis.clear()
        self.discordantAxis.set_title("Discordant distribution")
        self.discordantAxis.set_xlabel("Age (Ma)")
        self.discordantAxis.set_xlim(*self._age_xlim)
        self.discordantAxis.set_ylim(0, 1.0)
        self.discordantAxis.hist(scaledValues, bins=self._bars, cumulative=True, weights=weights, range=(self._barMin, self._barMax))

    def plotStatistics(self, statistics):
        xs = [age/(10**6) for age in statistics.keys()]
        ys = list(statistics.values())

        self.statisticAxis.clear()
        self.statisticAxis.set_title("KS statistic")
        self.statisticAxis.set_xlabel("Age (Ma)")
        self.statisticAxis.set_ylabel("p value")
        self.statisticAxis.set_xlim(*self._age_xlim)
        self.statisticAxis.set_ylim((0,self._statistic_ymax))
        self.statisticAxis.plot(xs, ys)

        self.statisticAxis.chosenAgeLine = self.statisticAxis.plot([],[])[0]

        self.canvas.draw()

    def plotAgeComparison(self, rimAge, ages):
        self.plotDiscordantHistogram(ages)

        scaledAge = rimAge/(10**6)
        self.statisticAxis.chosenAgeLine.set_xdata([scaledAge, scaledAge])
        self.statisticAxis.chosenAgeLine.set_ydata([0, self._statistic_ymax])

        uPb = calculations.u238pb206_from_age(rimAge)
        pbPb = calculations.pb207pb206_from_age(rimAge)
        self.concordiaAxis.chosenAgePoint.set_xdata([uPb])
        self.concordiaAxis.chosenAgePoint.set_ydata([pbPb])
        self.canvas.draw()

    def onProcessingProgress(self, i, *args):
        pass

    #######################
    ## Mouse interaction ##
    #######################

    def onMouseEnterAxes(self, event):
        self.mouseOnStatisticsAxes = event.inaxes == self.statisticAxis

    def onMouseExitAxes(self, event):
        if self.mouseOnStatisticsAxes:
            self.mouseOnStatisticsAxes = False
            self.controller.selectAgeToCompare(None)

    def onHover(self, event):
        if not self.mouseOnStatisticsAxes:
            return

        x, y = self.statisticAxis.transData.inverted().transform([(event.x, event.y)]).ravel()
        chosenAge = x * (10**6)
        self.controller.selectAgeToCompare(chosenAge)
