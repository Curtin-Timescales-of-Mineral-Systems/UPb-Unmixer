from apps.abstract.helpDialog import AbstractHelpDialog
from utils import calculations, stringUtils


class UnmixHelpDialog(AbstractHelpDialog):
    def __init__(self):
        super().__init__()

    def getTitle(self):
        return "U-Pb Unmixer"

    def getInputsHelpText(self):
        return \
            "Input data required: <ul>" \
            "<li> known age (in Ma) of rim (younger) component in mixture" \
            "<li> measured ²³⁸U/²⁰⁶Pb and ²⁰⁷Pb/²⁰⁶Pb ratios" \
            "<li> uncertainties for all of the above" \
            "</ul>" \
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
            "If a row in the imported data is invalid then it will be highlighted in <font color='red'>RED</font>."

    def getProcessingHelpText(self):
        return \
            "Processing the data will attempt to calculate a reconstructed core age with associated uncertainty values." \
            "<br><br>" \
            "Uncertainties are calculated using second order error propagation. " \
            "Due to the non-linearity of the concordia curve, the resulting uncertainties are not symmetric. " \
            "In particular the upper uncertainty will be larger than the lower uncertainty." \
            "<br><br>" \
            "Rows with successful calculations will be highlighted in <font color='green'>GREEN</font>." \
            "<br><br>" \
            "Rows with partially successful calculations will be highlighted in <font color='orange'>ORANGE</font>." \
            "<br><br>" \
            "Constants used:" \
            "<ul>" \
            "<li> ²³⁸U/²³⁵U ratio " + "&nbsp;"*10 + " = " + stringUtils.getConstantStr(calculations.U238U235_RATIO) + \
            "<li> ²³⁸U decay constant = " + stringUtils.getConstantStr(calculations.U238_DECAY_CONSTANT) + \
            "<li> ²³⁵U decay constant = " + stringUtils.getConstantStr(calculations.U235_DECAY_CONSTANT) + \
            "<ul>"

    def getOutputsHelpText(self):
        return \
            "The following values are output:" \
            "<ul>" \
            "<li> a reconstructed core age (in Ma)" \
            "<li> reconstructed core ²³⁸U/²⁰⁶Pb and ²⁰⁷Pb/²⁰⁶Pb ratios " \
            "<li> uncertainties for all of the above" \
            "</ul>" \
            "Clicking on an individual row permits visual inspection of the full solution " \
            "on the inverse Concordia plot." \
            "<br><br>" \
            "Selecting multiple rows permits visual inspection of the final calculated ages of " \
            "all the rows in the selection." \
            "<br><br>" \
            "The concordia plot may be fully customised (markers, colours, scale etc.) using the " \
            "tools at the bottom of the plot. The plot can also be saved to various image formats." \
            "<br><br>" \
            "When the calculated values are exported back to a CSV file, the values are appended to the end of the " \
            "columns of the original CSV file."