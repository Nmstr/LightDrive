from .abstract_desk_item import AbstractDeskItem
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGraphicsTextItem, QDialogButtonBox, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QStaticText, QPen

class DeskLabelConfig(QDialog):
    def __init__(self, window, text: str) -> None:
        """
        Create a dialog for configuring a label
        :param window: The main window
        :param text: The text of the label
        """
        super().__init__()
        self.window = window
        self.text = text

        self.setWindowTitle("LightDrive - Label Properties")

        layout = QVBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setText(self.text)
        self.label_edit.setPlaceholderText("Label text")
        layout.addWidget(self.label_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

class DeskLabel(AbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int, uuid: str, text: str = "Label") -> None:
        """
        Create a label object
        :param desk: The control desk object
        :param x: The x position of the label
        :param y: The y position of the label
        :param width: The width of the label
        :param height: The height of the label
        :param uuid: The UUID of the label
        :param text: The text on the label
        """
        super().__init__(desk, x, y, width, height, uuid)
        self.desk = desk
        self.text = text

        self.label = QGraphicsTextItem(self.text)
        self.label.setPos(x, y)  # Center the label inside the rect
        self.label.setDefaultTextColor(Qt.black)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        super().paint(painter, option, widget)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawStaticText(0, 0, QStaticText(self.text))

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the label's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskLabelConfig(window=self.desk.window, text=self.text)
        if config_dlg.exec():
            self.text = config_dlg.label_edit.text()
            self.label.setPlainText(config_dlg.label_edit.text())
        super().mouseDoubleClickEvent(event)
