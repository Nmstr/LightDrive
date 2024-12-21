from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt

class DeskButton(QGraphicsRectItem):
    def __init__(self, desk, x, y, width, height) -> None:
        """
        Create a button object
        """
        super().__init__(x, y, width, height)
        self.desk = desk
        self.pressed = False
        self.setBrush(Qt.lightGray)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Activate or deactivate the button
        """
        if not self.desk.window.live_mode:
            return  # Disallow button press outside live mode

        self.pressed = not self.pressed
        if self.pressed:
            self.setBrush(Qt.darkGray)
            self.setPen(QPen(Qt.green, 2))
        else:
            self.setBrush(Qt.lightGray)
            self.setPen(QPen(Qt.black, 1))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the button's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        """
        Move the button
        """
        if self.desk.window.live_mode:
            return  # Disable movement in live mode
        super().mouseMoveEvent(event)

class ControlDesk(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the control desk object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)

    def add_btn(self) -> None:
        """
        Add a button to the control desk
        """
        button = DeskButton(self, 0, 0, 100, 100)
        self.scene.addItem(button)

    def add_fader(self) -> None:
        """
        Add a slider to the control desk
        """
        pass

    def add_knob(self) -> None:
        """
        Add a knob to the control desk
        """
        pass

    def add_sound_trigger(self) -> None:
        """
        Add a sound trigger to the control desk
        """
        pass

    def add_label(self) -> None:
        """
        Add a label to the control desk
        """
        pass

    def add_clock(self) -> None:
        """
        Add a clock to the control desk
        """
        pass
