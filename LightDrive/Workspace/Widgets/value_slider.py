from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QSizePolicy, QSpinBox, QLabel
from PySide6.QtGui import QPainter, QPixmap, QPalette, QColor
from PySide6.QtCore import Qt
import json
import os

class JumpSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):  # noqa: N802
        inverted_pos = (event.pos().y() * -1) + self.height()
        reduced_position = inverted_pos / self.height()
        self.setValue(reduced_position * self.maximum())
        super().mousePressEvent(event)

class ResetButton(QWidget):
    def __init__(self, parent=None):
        self.value_slider = parent
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.icon = QPixmap("Assets/Icons/reset_button.svg")

    def mousePressEvent(self, event):  # noqa: N802
        self.value_slider.reset_value()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        """
        Paint the button
        :return: None
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self.rect(), self.icon)
        super().paintEvent(event)

class SliderIcon(QWidget):
    def __init__(self, parent = None):
        self.value_slider = parent
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.icon = None
        self.update_icon()

    def update_icon(self, fixture_id: int = None, fixture_address: int = None) -> None:
        """
        Updates the icon of the widget
        :param fixture_id: The id of the fixture
        :param fixture_address: The address of the fixture
        :return: None
        """
        if not fixture_id or fixture_address is None:
            self.hide()
            return

        # Get fixture data
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(f"{fixture_dir}/{fixture_id}.json")) as f:
            fixture_data = json.load(f)

        # Return if the position is wrong
        relative_position = self.value_slider.index + 1 - fixture_address
        if relative_position < 0:
            return  # Return if position too low
        if relative_position > len(fixture_data["channels"]) - 1:
            return  # Return if position higher than max channel

        # Update the icon
        channel_data = fixture_data["channels"][str(relative_position)]
        self.icon = QPixmap(f"Assets/Icons/{channel_data["type"].lower()}.svg")
        self.show()

    def paintEvent(self, event) -> None:  # noqa: N802
        """
        Paint the button
        :return: None
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self.rect(), self.icon)
        super().paintEvent(event)

class ValueSlider(QWidget):
    def __init__(self, parent=None, index: int = 0):
        self.workspace_window = parent
        self.index = index
        self.value_in_universe = {}
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.set_color()

        layout = QVBoxLayout()

        reset_button = ResetButton(self)
        layout.addWidget(reset_button)

        self.number_display = QSpinBox(self)
        self.number_display.setRange(0, 255)
        self.number_display.valueChanged.connect(self.set_value)
        layout.addWidget(self.number_display)

        self.slider = JumpSlider(self)
        self.slider.setRange(0, 255)
        self.slider.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.slider.valueChanged.connect(self.set_value)
        layout.addWidget(self.slider)

        label = QLabel(self)
        label.setText(str(self.index + 1))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.icon = SliderIcon(self)
        layout.addWidget(self.icon)

        self.setLayout(layout)

    def set_value(self, value: int) -> None:
        """
        Sets the value of the slider
        :param value: The integer value to be set
        :return: None
        """
        self.slider.setValue(value)
        self.number_display.setValue(value)
        self.workspace_window.dmx_output.set_single_value(universe = self.workspace_window.console_current_universe,
                                                          channel = self.index + 1,
                                                          value = value)
        self.set_color("#2a4129")
        self.value_in_universe[self.workspace_window.console_current_universe] = value

    def update_universe(self):
        """
        Updates the universe of the slider to the current one
        :return: None
        """
        if self.workspace_window.console_current_universe in self.value_in_universe:
            value = self.value_in_universe[self.workspace_window.console_current_universe]
            if value == 0:
                self.reset_value()
            else:
                self.set_value(self.value_in_universe[self.workspace_window.console_current_universe])
        else:
            self.reset_value()

    def reset_value(self) -> None:
        """
        Resets the value of the slider
        :return: None
        """
        self.slider.setValue(0)
        self.number_display.setValue(0)
        self.set_color()

    def set_color(self, color: str = "#2c3035") -> None:
        """
        Sets the color of the slider
        :param color: The hex value to be set (default: "#2c3035")
        :return:
        """
        pal = QPalette()
        pal.setColor(self.backgroundRole(), QColor(color))
        self.setPalette(pal)

    def update_icon(self):
        """
        Updates the icon of the slider
        :return: None
        """
        self.icon.update_icon()
        available_fixtures = self.workspace_window.available_fixtures
        for fixture in available_fixtures:
            if not fixture["universe"] == self.workspace_window.console_current_universe:
                continue
            self.icon.update_icon(fixture["id"], fixture["address"])
