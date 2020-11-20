from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator, QPalette, QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget

FORM_HORIZONTAL_SPACING = 15


def attachValidator(widget, regex):
    widget.setValidator(None)
    validator = QRegExpValidator(regex)
    widget.setValidator(validator)


def colour(widget, color):
    palette = QPalette()
    palette.setColor(QPalette.Window, color)
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)


def retainSizeWhenHidden(widget):
    policy = widget.sizePolicy()
    policy.setRetainSizeWhenHidden(True)
    widget.setSizePolicy(policy)


def getTextWidth(text):
    font_metrics = QFontMetrics(QFont())
    return font_metrics.horizontalAdvance(text)


def createIconWithLabel(icon, text):
    icon_label = QLabel()
    icon_label.setPixmap(icon.pixmap(16, 16))
    text_label = QLabel(text)
    text_label.setAlignment(Qt.AlignLeft)

    layout = QHBoxLayout()
    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.addStretch()
    layout.setContentsMargins(0, 0, 0, 0)

    widget = QWidget()
    widget.setLayout(layout)
    widget.setContentsMargins(0, 0, 0, 0)
    return widget, text_label
