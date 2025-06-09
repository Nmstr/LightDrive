from .input_item import InputItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from enum import Enum

class InputState(Enum):
    FALSE = 0
    TRUE = 1
    EXTERNAL = 2

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
