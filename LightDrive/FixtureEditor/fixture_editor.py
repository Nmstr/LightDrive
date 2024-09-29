from open_fixture_dialog import OpenFixtureDialog
from save_error_dialog import SaveErrorDialog
from channel_entry import ChannelEntry
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import json
import sys
import os

def is_alphanumeric_with_spaces(string) -> bool:
    """
    Checks if a string is alphanumeric (allows spaces)
    :param string: The string to check
    :return: Whether the string is alphanumeric
    """
    for char in string:
        if not (char.isalnum() or char.isspace()):
            return False
    return True

def clear_field(container: str, target_layout, *, amount_left: int = 1):
    """
    Clear a container of its contents
    :param container: The container to clear
    :param target_layout: The layout that should be added if none exists (e.g. QVboxLayout, QHboxLayout...)
    :param amount_left: The amount of elements that should be kept
    :return: None
    """
    # Check if the container has a layout, if not, set a new layout of type target_layout
    layout = container.layout()
    if layout is None:
        layout = target_layout
        container.setLayout(layout)

    while layout.count() > amount_left:
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
    return layout

class FixtureEditor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("FixtureEditor")
        self.setWindowTitle("LightDrive - Fixture Editor")
        self.file_path = None
        self.channels = []

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("FixtureEditor/fixture_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        self.ui.add_channel_btn.clicked.connect(lambda: self.add_channel())
        self.ui.open_btn.clicked.connect(lambda: self.open_fixture())
        self.ui.save_btn.clicked.connect(lambda: self.save_fixture())

    def add_channel(self, channel_name = None,
                 minimum_value = None,
                 maximum_value = None,
                 description = None) -> None:
        """
        Add a channel to the fixture
        :return: None
        """
        layout = self.ui.channel_container.layout()
        channel_entry = ChannelEntry(channel_name, minimum_value, maximum_value, description)
        layout.insertWidget(layout.count() - 1, channel_entry)
        self.channels.append(channel_entry)

    def open_fixture(self) -> None:
        """
        Open a fixture
        :return: None
        """
        # Ask which fixture to open
        dlg = OpenFixtureDialog()
        if not dlg.exec():
            return
        # Check if the fixture exists
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        fixture_path = os.path.join(fixture_dir, dlg.clicked_fixture)
        if not os.path.exists(fixture_path):
            return

        # Load the fixtures data
        with open(fixture_path, 'r') as f:
            fixture_data = json.loads(f.read())

        # Set the fixture data
        self.ui.name_edit.setText(fixture_data["name"])
        self.ui.manufacturer_edit.setText(fixture_data["manufacturer"])
        self.ui.width_spin.setValue(fixture_data["width"])
        self.ui.height_spin.setValue(fixture_data["height"])
        self.ui.length_spin.setValue(fixture_data["length"])
        self.ui.weight_dspin.setValue(fixture_data["weight"])
        self.ui.illuminant_type_edit.setText(fixture_data["illuminant_type"])
        self.ui.lumen_spin.setValue(fixture_data["lumen"])
        self.ui.temp_spin.setValue(fixture_data["temp"])
        self.ui.wattage_spin.setValue(fixture_data["wattage"])
        self.ui.head_type_combo.setCurrentText(fixture_data["head_type"])
        self.ui.max_pan_spin.setValue(fixture_data["max_pan"])
        self.ui.max_tilt_spin.setValue(fixture_data["max_tilt"])
        self.ui.power_spin.setValue(fixture_data["power"])
        self.ui.dmx_type_combo.setCurrentText(fixture_data["dmx_type"])
        # Set the channels
        channels = fixture_data.get("channels", {})
        clear_field(self.ui.channel_container, QVBoxLayout())
        for channel_index, channel_data in channels.items():
            self.add_channel(channel_data["name"], channel_data["minimum"], channel_data["maximum"], channel_data["description"])
        self.file_path = fixture_path

    def save_fixture(self) -> None:
        """
        Save the current fixture
        :return: None
        """
        # Check if fixture can be saved
        fixture_name = self.ui.name_edit.text()
        print(fixture_name)
        if fixture_name == "":
            SaveErrorDialog("The fixture name can not be empty.").exec()
            return
        if not is_alphanumeric_with_spaces(fixture_name):
            SaveErrorDialog("The fixture name needs to be alphanumeric (+ spaces).").exec()
            return
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        fixture_path = os.path.join(fixture_dir, f"{fixture_name}.json")
        if os.path.exists(fixture_path) and self.file_path != fixture_path:
            SaveErrorDialog("This fixture already exists. If you intended to edit it, open it first.").exec()
            return
        self.file_path = fixture_path  # This allows the fixture to be resaved, while still disallowing it to be overwritten when not opened
        os.makedirs(fixture_dir, exist_ok=True)

        # Create main fixture data dict
        fixture_data = {
            "name": fixture_name,
            "manufacturer": self.ui.manufacturer_edit.text(),
            "width": self.ui.width_spin.value(),
            "height": self.ui.height_spin.value(),
            "length": self.ui.length_spin.value(),
            "weight": self.ui.weight_dspin.value(),
            "illuminant_type": self.ui.illuminant_type_edit.text(),
            "lumen": self.ui.lumen_spin.value(),
            "temp": self.ui.temp_spin.value(),
            "wattage": self.ui.wattage_spin.value(),
            "head_type": self.ui.head_type_combo.currentText(),
            "max_pan": self.ui.max_pan_spin.value(),
            "max_tilt": self.ui.max_tilt_spin.value(),
            "power": self.ui.power_spin.value(),
            "dmx_type": self.ui.dmx_type_combo.currentText(),
            "channels": {},
        }

        # Append channels
        for i, channel in enumerate(self.channels):
            channel_data = channel.get_data()
            if channel_data["name"] == "":
                SaveErrorDialog("All channels need to be named").exec()
                return
            fixture_data["channels"][i] = channel_data

        with open(fixture_path, 'w') as f:
            f.write(json.dumps(fixture_data, indent=4))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FixtureEditor()
    window.show()
    sys.exit(app.exec())
