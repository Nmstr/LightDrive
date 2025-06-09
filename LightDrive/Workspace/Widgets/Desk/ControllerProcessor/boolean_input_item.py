from .input_item import InputItem
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QComboBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from enum import Enum

class InputState(Enum):
    FALSE = 0
    TRUE = 1
    EXTERNAL = 2

class BooleanInputItemConfig(QDialog):
    def __init__(self, window, input_state: InputState) -> None:
        """
        Create a dialog for configuring a boolean input item
        :param window: The main window
        :param input_state: The current state of the input
        """
        super().__init__()
        self.window = window
        self.input_state = input_state

        self.setWindowTitle("LightDrive - Boolean Input Properties")

        layout = QVBoxLayout()
        self.state_label = QLabel(self)
        self.state_label.setText("Input State:")
        layout.addWidget(self.state_label)
        self.input_state_combo = QComboBox()
        self.input_state_combo.addItem("False", InputState.FALSE)
        self.input_state_combo.addItem("True", InputState.TRUE)
        self.input_state_combo.addItem("External", InputState.EXTERNAL)
        self.input_state_combo.setCurrentIndex(self.input_state.value)
        layout.addWidget(self.input_state_combo)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

class BooleanInputItem(InputItem):
    def __init__(self, processor_view, x: int, y: int, width: int, height: int, uuid: str, input_state: int) -> None:
        """
        Create a boolean input item for the controller processor
        :param processor_view: The processor view
        :param x: The x position of the boolean input item
        :param y: The y position of the boolean input item
        :param width: The width of the boolean input item
        :param height: The height of the boolean input item
        :param uuid: The uuid of the boolean input item
        :param input_state: The state of the input (0 for FALSE, 1 for TRUE, 2 for EXTERNAL)
        """
        super().__init__(processor_view, x, y, width, height, uuid)
        self.input_state = InputState(input_state) if input_state else InputState.FALSE

    def paint(self, painter: QPainter, option, widget=None, brush_color=Qt.lightGray) -> None:
        super().paint(painter, option, widget, brush_color=Qt.lightGray)
        if self.input_state == InputState.FALSE:
            painter.setBrush(Qt.red)
            label = "False"
        elif self.input_state == InputState.TRUE:
            painter.setBrush(Qt.green)
            label = "True"
        else:
            painter.setBrush(Qt.darkGray)
            label = "External"
        painter.drawEllipse(self.boundingRect().adjusted(10, 10, -10, -10))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, label)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the boolean input item's properties
        """
        config_dlg = BooleanInputItemConfig(window=self.desk.window, input_state=self.input_state)
        if config_dlg.exec():
            self.input_state = config_dlg.input_state_combo.currentData()
            self.update()
        super().mouseDoubleClickEvent(event)
