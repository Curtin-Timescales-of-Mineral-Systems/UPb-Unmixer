import argparse
import sys



from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

def createPanel():
    hbox = QHBoxLayout()
    """
    topleft = QFrame()
    topleft.setFrameShape(QFrame.StyledPanel)

    topright = QFrame()
    topright.setFrameShape(QFrame.StyledPanel)

    splitter1 = QSplitter(Qt.Horizontal)
    splitter1.addWidget(topleft)
    splitter1.addWidget(topright)

    hbox.addWidget(splitter1)
    """
    return hbox
    #    self.setLayout(hbox)

    #self.setGeometry(300, 300, 300, 200)
    #self.setWindowTitle('QSplitter')
    #self.show()


app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec_()

print("Hi")

"""
import csv_mode
import interactive_mode

mode_help="Either 'interactive' or 'csv'"
input_file_help = "The path for the input csv file."
output_file_help = "The path for the output csv file."
figures_help = "Generate figures as well as data"

parser = argparse.ArgumentParser()
parser.add_argument("mode", help=mode_help)
parser.add_argument("-f", "--figures", help=figures_help, action="store_true")
parser.add_argument("--input", help=input_file_help)
parser.add_argument("--output", help=output_file_help)
args = parser.parse_args()

def error(message):
    print(message)
    parser.print_help(sys.stderr)

if args.mode == "interactive":
    interactive_mode.run()
elif args.mode == "csv":
    if not args.input:
        error("No input file specified for CSV mode")
    elif not args.output:
        error("No output file specified for CSV mode")
    else:
        csv_mode.run(args.input, args.output, args.figures)
else:
    error("Unrecognised mode: " + args.mode)

"""