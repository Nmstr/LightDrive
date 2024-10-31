from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog
from PySide6.QtGui import QPalette, QColor, QMouseEvent
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

class UniverseConfigurationDialog(QDialog):
    def __init__(self, universe_index: int) -> None:
        """
        Creates the universe configuration dialog.
        :param universe_index: The index of the universe.
        """
        super().__init__()
        self.setWindowTitle("Universe Configuration")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Widgets/universe_configuration.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.ui.artnet_frame.setDisabled(True)

        self.ui.enable_artnet_checkbox.checkStateChanged.connect(self.switch_artnet_state)
        self.ui.apply_btn.clicked.connect(self.apply)
        self.ui.cancel_btn.clicked.connect(self.close)

        self.ui.universe_number_label.setText(f"Universe: {universe_index + 1}")

    def switch_artnet_state(self, state) -> None:
        """
        Switches the ArtNet state between activated and deactivated
        :param state: The new state of the enable_artnet_checkbox.
        :return: None
        """
        if state == state.Checked:
            self.ui.artnet_frame.setDisabled(False)
        else:
            self.ui.artnet_frame.setDisabled(True)

    def apply(self) -> None:
        """
        Applies the changes made to the configuration
        :return: None
        """
        super().accept()

class UniverseEntry(QWidget):
    def __init__(self, parent=None, universe_index: int = 0):
        self.universe_index = universe_index
        self.workspace_window = parent
        super().__init__(parent)
        self.setObjectName("UniverseEntry")
        self.setFixedHeight(100)
        self.setAutoFillBackground(True)
        self.set_color()

        layout = QVBoxLayout()

        label = QLabel(self)
        label.setText(f"Universe: {self.universe_index + 1}")
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

    def mousePressEvent(self, event: QMouseEvent):  # noqa: N802
        self.set_color("#2a4129")
        self.workspace_window.select_io_universe(self.universe_index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):  # noqa: N802
        dlg = UniverseConfigurationDialog(self.universe_index)
        if dlg.exec_():
            print("Accepted")
        super().mouseDoubleClickEvent(event)
