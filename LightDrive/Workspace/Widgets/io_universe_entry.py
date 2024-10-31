from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QSizePolicy, QSpinBox, QLabel, QDialog, QDialogButtonBox, QPushButton
from PySide6.QtGui import QPainter, QPixmap, QPalette, QColor, QMouseEvent
from PySide6.QtCore import Qt, QSize

class UniverseEntry(QWidget):
    def __init__(self, parent=None, universe_number: int = 0):
        self.universe_number = universe_number
        self.workspace_window = parent
        super().__init__(parent)
        self.setObjectName("UniverseEntry")
        self.setFixedHeight(100)
        self.setAutoFillBackground(True)
        self.set_color()

        layout = QVBoxLayout()

        label = QLabel(self)
        label.setText(f"Universe: {self.universe_number + 1}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

    def deselect(self) -> None:
        """
        Deselects the currently selected universe entry.
        :return: None
        """
        self.set_color()

    def set_color(self, color: str = "#2c3035") -> None:
        """
        Sets the color of the slider
        :param color: The hex value to be set (default: "#2c3035")
        :return: None
        """
        pal = QPalette()
        pal.setColor(self.backgroundRole(), QColor(color))
        self.setPalette(pal)

    def mousePressEvent(self, event: QMouseEvent):
        self.set_color("#2a4129")
        self.workspace_window.select_io_universe(self.universe_number)
        super().mousePressEvent(event)
