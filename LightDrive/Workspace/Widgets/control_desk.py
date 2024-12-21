from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene

class ControlDesk(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the timeline object
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
        pass

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
