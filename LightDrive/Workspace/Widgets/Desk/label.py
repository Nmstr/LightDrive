from .abstract_desk_item import AbstractDeskItem
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGraphicsTextItem, QDialogButtonBox, QLineEdit
from PySide6.QtCore import Qt

class DeskLabelConfig(QDialog):
    def __init__(self, window, label_text: str) -> None:
        """
        Create a dialog for configuring a label
        :param window: The main window
        :param label_text: The text of the label
        """
        super().__init__()
        self.window = window
        self.label_text = label_text

        self.setWindowTitle("LightDrive - Label Properties")

        layout = QVBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setText(self.label_text)
        self.label_edit.setPlaceholderText("Label text")
        layout.addWidget(self.label_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

class DeskLabel(AbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int, label_uuid: str, label_text: str = "Label") -> None:
        """
        Create a label object
        :param desk: The control desk object
        :param x: The x position of the label
        :param y: The y position of the label
        :param width: The width of the label
        :param height: The height of the label
        :param label_uuid: The UUID of the label
        :param label_text: The text on the label
        """
        super().__init__(desk, x, y, width, height)
        self.desk = desk
        self.label_text = label_text
        self.label_uuid = label_uuid

        self.label = QGraphicsTextItem(self.label_text)
        self.label.setPos(x, y)  # Center the label inside the rect
        self.label.setDefaultTextColor(Qt.black)
        self.addToGroup(self.label)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the label's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskLabelConfig(window=self.desk.window, label_text=self.label_text)
        if config_dlg.exec():
            self.label_text = config_dlg.label_edit.text()
            self.label.setPlainText(config_dlg.label_edit.text())
        super().mouseDoubleClickEvent(event)
