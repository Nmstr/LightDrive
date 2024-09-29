from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QHBoxLayout, QWidget, QSpinBox

class ChannelEntry(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChannelEntry")

        self.ui = QWidget(self)
        self.ui.layout = QHBoxLayout(self)
        # Channel Name
        self.ui.name_edit = QLineEdit(self)
        self.ui.name_edit.setPlaceholderText("Channel Name")
        self.ui.layout.addWidget(self.ui.name_edit)
        # Minimum Value
        self.ui.minimum_label = QLabel("Minimum Value:", self)
        self.ui.layout.addWidget(self.ui.minimum_label)
        self.ui.minimum_spin = QSpinBox(self)
        self.ui.minimum_spin.setMinimum(0)
        self.ui.minimum_spin.setMaximum(255)
        self.ui.layout.addWidget(self.ui.minimum_spin)
        # Maximum Value
        self.ui.maximum_label = QLabel("Maximum Value:", self)
        self.ui.layout.addWidget(self.ui.maximum_label)
        self.ui.maximum_spin = QSpinBox(self)
        self.ui.maximum_spin.setMinimum(0)
        self.ui.maximum_spin.setMaximum(255)
        self.ui.layout.addWidget(self.ui.maximum_spin)
        # Description
        self.ui.description = QLineEdit(self)
        self.ui.description.setPlaceholderText("Channel Description")
        self.ui.layout.addWidget(self.ui.description)

    def get_data(self) -> dict:
        channel_data = {
            "name": self.ui.name_edit.text(),
            "minimum": self.ui.minimum_spin.value(),
            "maximum": self.ui.maximum_spin.value(),
            "description:": self.ui.description.text()
        }
        return channel_data
