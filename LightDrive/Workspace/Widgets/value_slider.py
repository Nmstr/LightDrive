from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QSizePolicy, QSpinBox, QLabel
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt

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
        self.parent = parent
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.icon = QPixmap("Assets/Icons/reset_button.svg")

    def mousePressEvent(self, event):  # noqa: N802
        self.parent.slider.setValue(0)
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

class ValueSlider(QWidget):
    def __init__(self, parent=None, index: int = 0):
        super().__init__(parent)
        layout = QVBoxLayout()

        reset_button = ResetButton(self)
        layout.addWidget(reset_button)

        self.number_display = QSpinBox(self)
        self.number_display.setRange(0, 255)
        self.number_display.valueChanged.connect(lambda: self.slider.setValue(self.number_display.value()))
        layout.addWidget(self.number_display)

        self.slider = JumpSlider(self)
        self.slider.setRange(0, 255)
        self.slider.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.slider.valueChanged.connect(self.number_display.setValue)
        layout.addWidget(self.slider)

        label = QLabel(self)
        label.setText(str(index + 1))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)
