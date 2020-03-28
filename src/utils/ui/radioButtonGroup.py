from PyQt5.QtWidgets import QWidget, QButtonGroup, QHBoxLayout, QRadioButton


class RadioButtonGroup(QWidget):

    def __init__(self, options, validation, default):
        super().__init__()

        self.options = options
        self.group = QButtonGroup()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        for i, option in enumerate(options):
            button = QRadioButton(option)
            button.option = option
            button.setChecked(option == default)
            layout.addWidget(button)
            self.group.addButton(button, i)
        self.group.buttonReleased.connect(validation)

        self.setLayout(layout)

    def getSelection(self):
        return self.options[self.group.checkedId()]


class IntRadioButtonGroup(RadioButtonGroup):

    def __init__(self, options, validation, default):
        optionsStr = [str(v) for v in options]
        defaultStr = str(default)
        super().__init__(optionsStr, validation, defaultStr)

    def getSelection(self):
        return int(super().getSelection())