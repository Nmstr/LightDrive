from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

class UniverseConfigurationDialog(QDialog):
    def __init__(self, universe_data: dict) -> None:
        """
        Creates the universe configuration dialog.
        :param universe_data: The current data of the universe
        """
        super().__init__()
        self.setWindowTitle("Universe Configuration")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Widgets/universe_configuration.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        artnet_config = universe_data.get("ArtNet")
        self.ui.artnet_frame.setDisabled(not artnet_config.get("active"))
        self.ui.enable_artnet_checkbox.setChecked(artnet_config.get("active"))
        self.ui.target_ip_edit.setText(artnet_config.get("target_ip"))
        self.ui.universe_spin.setValue(artnet_config.get("universe"))

        self.ui.enable_artnet_checkbox.checkStateChanged.connect(self.switch_artnet_state)
        self.ui.apply_btn.clicked.connect(self.apply)
        self.ui.cancel_btn.clicked.connect(self.close)

        self.ui.universe_number_label.setText(universe_data.get("name"))

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
    def __init__(self, window, universe_uuid: str, universe_name: str):
        self.workspace_window = window
        self.universe_uuid = universe_uuid
        self.universe_name = universe_name
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel(self)
        label.setText(universe_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event: QMouseEvent):  # noqa: N802
        universe_data = self.workspace_window.dmx_output.get_universe_configuration(self.universe_uuid)
        dlg = UniverseConfigurationDialog(universe_data)

        if dlg.exec_():
            self.workspace_window.dmx_output.configure_artnet(universe_uuid = self.universe_uuid,
                                                              active = dlg.ui.enable_artnet_checkbox.isChecked(),
                                                              target_ip = dlg.ui.target_ip_edit.text(),
                                                              artnet_universe = dlg.ui.universe_spin.value(),
                                                              hz = dlg.ui.hz_spin.value())
        super().mouseDoubleClickEvent(event)
