from .abstract_desk_item import AbstractDeskItem
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGraphicsTextItem, QDialogButtonBox, QSpinBox, QLabel
from PySide6.QtCore import Qt, QTimer
import datetime

class DeskClockConfig(QDialog):
    def __init__(self, window, polling_rate: int) -> None:
        """
        Create a dialog for configuring a clock
        :param window: The main window
        :param polling_rate: The rate at which the clock updates
        """
        super().__init__()
        self.window = window
        self.polling_rate = polling_rate

        self.setWindowTitle("LightDrive - Clock Properties")

        layout = QVBoxLayout()
        self.label = QLabel("Polling Rate (ms):")
        layout.addWidget(self.label)
        self.polling_rate_edit = QSpinBox()
        self.polling_rate_edit.setRange(1, 32767)
        self.polling_rate_edit.setValue(self.polling_rate)
        layout.addWidget(self.polling_rate_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

class DeskClock(AbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int, clock_uuid: str, polling_rate: int) -> None:
        """
        Create a label object
        :param desk: The control desk object
        :param x: The x position of the label
        :param y: The y position of the label
        :param width: The width of the label
        :param height: The height of the label
        :param clock_uuid: The UUID of the label
        :param polling_rate: The rate at which the clock updates
        """
        super().__init__(desk, x, y, width, height)
        self.desk = desk
        self.clock_uuid = clock_uuid
        self.polling_rate = polling_rate

        self.label = QGraphicsTextItem("00:00:00")
        self.label.setPos(x, y)  # Center the label inside the rect
        self.label.setDefaultTextColor(Qt.black)
        self.addToGroup(self.label)
        self.update_time()

        self.timer = QTimer()
        self.timer.setInterval(self.polling_rate)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(self.polling_rate)

    def update_time(self) -> None:
        """
        Update the time on the clock
        """
        self.label.setPlainText(datetime.datetime.now().strftime("%H:%M:%S"))

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the label's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskClockConfig(window=self.desk.window, polling_rate=self.polling_rate)
        if config_dlg.exec():
            self.polling_rate = config_dlg.polling_rate_edit.value()
            self.timer.setInterval(self.polling_rate)
        super().mouseDoubleClickEvent(event)
