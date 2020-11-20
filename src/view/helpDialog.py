from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget, QDialog, QLayout

from utils import config, string, calculations


class HelpDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.TITLE + " help")

        about_label: QLabel = QLabel(self.getAboutHelpText())
        about_label.title = "About"

        inputs_label: QLabel = QLabel(self.getInputsHelpText())
        inputs_label.title = "Inputs"

        processing_label: QLabel = QLabel(self.getProcessingHelpText())
        processing_label.title = "Processing"

        outputs_label: QLabel = QLabel(self.getOutputsHelpText())
        outputs_label.title = "Outputs"

        tab_widget = QTabWidget()
        for label in [about_label, inputs_label, processing_label, outputs_label]:
            label.setTextFormat(Qt.RichText)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse|label.textInteractionFlags())
            layout = QVBoxLayout()
            layout.addWidget(label, 0, Qt.AlignTop)
            widget = QWidget()
            widget.setLayout(layout)
            tab_widget.addTab(widget, label.title)

        layout: QLayout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)

    def _getStandardInputHelp(self) -> str:
        return \
            "Data can be parsed from a range of csv file layouts by specifying which columns the required values are " \
            "in. Columns can be referred to either by using:" \
            "<ul>" \
            "  <li> numbers (1, 2, 3, ..., 26, 27, ...)" \
            "  <li> letters (A, B, C, ..., Z, AA, ...)" \
            "</ul>" \
            "Different uncertainty formats are also supported:" \
            "<ul>" \
            "  <li> percentage vs absolute" \
            "  <li> 1σ vs 2σ" \
            "</ul>" \
            "If a row in the imported data is invalid then it will be highlighted in <font color='red'>RED</font>." \
            "<br>" \
            "Symbols are not supported in column headings (e.g., ±, σ). Use only English alphabetic characters or " \
            "numerals."

    def _getStandardProcessingHelp(self) -> str:
        return \
            "Constants used:" \
            "<ul>" \
            "<li> ²³⁸U/²³⁵U ratio " + "&nbsp;" * 9 + " = " + string.getConstantStr(calculations.U238U235_RATIO) + \
            "<li> ²³⁸U decay constant " + "&nbsp;" * 1 + " = " + string.getConstantStr(calculations.U238_DECAY_CONSTANT) + \
            "<li> ²³⁵U decay constant " + "&nbsp;" * 1 + " = " + string.getConstantStr(calculations.U235_DECAY_CONSTANT) + \
            "<li> ²³²Th decay constant = " + string.getConstantStr(calculations.TH232_DECAY_CONSTANT) + \
            "<li> Avogadro constant " + "&nbsp;" * 3 + " = " + string.getConstantStr(calculations.AVOGADRO_NUMBER) + \
            "<ul>"

    def _getStandardOutputsHelp(self) -> str:
        return \
            "The plot may be fully customised (markers, colours, scale etc.) using the " \
            "button in the toolbar at the bottom. The plot can also be saved to various image formats." \
            "<br><br>" \
            "When the calculated values are exported back to a CSV file, the values are appended to the end of the " \
            "columns of the original CSV file."

    def getInputsHelpText(self) -> str:
        return \
            "Input data required: <ul>" \
            "<li> known age (in Ma) of rim (younger) component in mixture" \
            "<li> measured ²³⁸U/²⁰⁶Pb and ²⁰⁷Pb/²⁰⁶Pb ratios" \
            "<li> uncertainties for all of the above" \
            "<li> U and Th concentrations (ppm)" \
            "</ul>" + \
            self._getStandardInputHelp()

    def getProcessingHelpText(self) -> str:
        return \
            "Processing the data will attempt to calculate a reconstructed core age with associated uncertainty values." \
            "<br><br>" \
            "Uncertainties are calculated using second order error propagation. " \
            "Due to the non-linearity of the concordia curve, the resulting uncertainties are not symmetric. " \
            "In particular the upper uncertainty will be larger than the lower uncertainty." \
            "<br><br>" \
            "Rows with unsuccessful calculations will be highlighted in <font color='" + config.INVALID_CALCULATION_COLOUR + "'>ORANGE</font>." \
            "<br><br>" \
            "Rows with successful calculations that have a total score of &#60; 0.5 will be highlighted in <font color='" + config.REJECTED_CALCULATION_COLOUR + "'>YELLOW</font>." \
            "<br><br>" \
            "Rows with successful calculations that have a total score of >= 0.5 will be highlighted in <font color='" + config.VALID_CALCULATION_COLOUR + "'>GREEN</font>." \
            "<br><br>"  + \
            self._getStandardProcessingHelp()

    def getOutputsHelpText(self) -> str:
        return \
            "The following values are output:" \
            "<ul>" \
            "<li> a reconstructed core age (in Ma)" \
            "<li> reconstructed core ²³⁸U/²⁰⁶Pb and ²⁰⁷Pb/²⁰⁶Pb ratios " \
            "<li> uncertainties for all of the above" \
            "<li> metamict score for the reconstructed age" \
            "<li> precision score for the reconstructed age" \
            "<li> core:rim score for the reconstructed age" \
            "<li> total score for the reconstructed age" \
            "</ul>" \
            "Ages with a total score of &#60; 0.5 should be considered unreliable. " \
            "See the paper for more details on how individual scores are calculated." \
            "<br><br>" \
            "Clicking on an individual row permits visual inspection of the full solution " \
            "on the inverse Concordia plot. " \
            "Selecting multiple rows permits visual inspection of the final calculated ages of " \
            "all the rows in the selection." \
            "<br><br>"  + \
            self._getStandardOutputsHelp()

    def getAboutHelpText(self) -> str:
        link = "https://github.com/Curtin-Timescales-of-Mineral-Systems/UPb-Unmixer/issues"
        return \
            'This program is accompanied by the following paper which should be cited if it this program is used in your results' \
            '<p style="text-align: center">Hugo K.H. Olierook, Christopher L. Kirkland, Milo Barham,' \
            '<br>Matthew L. Daggitt, Julie Hollis, Michael Hartnady, ' \
            '<br>Extracting meaningful U-Pb ages from core–rim mixtures, Gondwana Research, 2020<\\p>' \
            '<br><br>' \
            'Please report any feedback or issues that you may have with this program on the ' \
            'Github page at: <p style="text-align: center"><a href="' + link + '">' + link + '</a><\\p>'