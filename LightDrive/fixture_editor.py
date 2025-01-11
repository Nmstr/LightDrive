from FixtureEditor.fixture_dialogs import OpenFixtureDialog
from FixtureEditor.fixture_dialogs import SaveErrorDialog
from FixtureEditor.fixture_dialogs import FixtureInfoDialog
from FixtureEditor.channel_editor import ChannelEditor
from Functions.ui import clear_field
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import configparser
import json
import sys
import os
import re

def is_valid_id(string) -> bool:
    """
    Checks if a string matches the following pattern: "^[A-Za-z0-9_-]*$"
    :param string: The string to check
    :return: Whether the string matches the pattern
    """
    if re.match("^[A-Za-z0-9_-]*$", string):
        return True
    return False

class ChannelEntry(QWidget):
    def __init__(self, parent = None, channel_data: dict = None):
        self.channel_data = channel_data
        self.parent = parent
        super().__init__(parent)

        name_label = QLabel(self)
        name_label.setText(self.channel_data["name"])
        type_label = QLabel(self)
        type_label.setText(self.channel_data["type"])
        remove_btn = QPushButton(self)
        remove_btn.setText("Remove Channel")
        remove_btn.clicked.connect(self.remove)

        layout = QHBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(type_label)
        layout.addWidget(remove_btn)
        self.setLayout(layout)

    def remove(self):
        self.parent.channels.remove(self)
        dlg = FixtureInfoDialog("You will need to save and re-open the fixture to remove the channel visually. It is recommended you do this immediately!",
                                width = 800)
        dlg.exec()

class FixtureEditor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LightDrive - Fixture Editor")
        self.file_path = None
        self.channels = []

        # Set the theme
        if os.path.isdir("/usr/lib/qt6/plugins"):
            app.addLibraryPath("/usr/lib/qt6/plugins")
        config = configparser.ConfigParser()
        config.read(os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/settings.ini')
        if "Settings" in config:
            app.setStyle(config["Settings"].get("theme", "Breeze"))


        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("FixtureEditor/fixture_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        self.ui.add_channel_btn.clicked.connect(lambda: self.add_channel())
        self.ui.open_btn.clicked.connect(lambda: self.open_fixture())
        self.ui.save_btn.clicked.connect(lambda: self.save_fixture())

    def add_channel(self) -> None:
        """
        Adds a new channel to the fixture
        :return: None
        """
        channel_editor = ChannelEditor()
        if not channel_editor.exec():
            return
        self.add_channel_widget(channel_editor.channel_data)

    def add_channel_widget(self, channel_data: dict):
        channel_entry = ChannelEntry(self, channel_data)
        layout = self.ui.channel_container.layout()
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
        self.ui.id_edit.setText(fixture_data["id"])
        self.ui.author_edit.setText(fixture_data["author"])
        self.ui.width_spin.setValue(fixture_data["width"])
        self.ui.height_spin.setValue(fixture_data["height"])
        self.ui.length_spin.setValue(fixture_data["length"])
        self.ui.weight_dspin.setValue(fixture_data["weight"])
        self.ui.illuminant_type_edit.setText(fixture_data["illuminant_type"])
        self.ui.lumen_spin.setValue(fixture_data["lumen"])
        self.ui.temp_spin.setValue(fixture_data["temp"])
        self.ui.wattage_spin.setValue(fixture_data["wattage"])
        self.ui.light_type_combo.setCurrentText(fixture_data["light_type"])
        self.ui.max_pan_spin.setValue(fixture_data["max_pan"])
        self.ui.max_tilt_spin.setValue(fixture_data["max_tilt"])
        self.ui.power_spin.setValue(fixture_data["power"])
        self.ui.dmx_type_combo.setCurrentText(fixture_data["dmx_type"])
        # Set the channels
        channels = fixture_data.get("channels", {})
        clear_field(self.ui.channel_container, QVBoxLayout())
        for channel_index, channel_data in enumerate(channels.items()):
            self.add_channel_widget(channel_data[1])
        self.file_path = fixture_path

    def save_fixture(self) -> None:
        """
        Save the current fixture
        :return: None
        """
        # Check if fixture can be saved
        fixture_id = self.ui.id_edit.text()
        if fixture_id == "":
            SaveErrorDialog("The fixture id can not be empty.").exec()
            return
        if not is_valid_id(fixture_id):
            SaveErrorDialog("The fixture id needs to match the following pattern: \"^[A-Za-z0-9_-]*$\"").exec()
            return
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        fixture_path = os.path.join(fixture_dir, f"{fixture_id}.json")
        if os.path.exists(fixture_path) and self.file_path != fixture_path:
            SaveErrorDialog("This fixture already exists. If you intended to edit it, open it first.").exec()
            return
        self.file_path = fixture_path  # This allows the fixture to be resaved, while still disallowing it to be overwritten when not opened
        os.makedirs(fixture_dir, exist_ok=True)

        # Create main fixture data dict
        fixture_data = {
            "name": self.ui.name_edit.text(),
            "manufacturer": self.ui.manufacturer_edit.text(),
            "id": fixture_id,
            "author": self.ui.author_edit.text(),
            "width": self.ui.width_spin.value(),
            "height": self.ui.height_spin.value(),
            "length": self.ui.length_spin.value(),
            "weight": self.ui.weight_dspin.value(),
            "illuminant_type": self.ui.illuminant_type_edit.text(),
            "lumen": self.ui.lumen_spin.value(),
            "temp": self.ui.temp_spin.value(),
            "wattage": self.ui.wattage_spin.value(),
            "light_type": self.ui.light_type_combo.currentText(),
            "max_pan": self.ui.max_pan_spin.value(),
            "max_tilt": self.ui.max_tilt_spin.value(),
            "power": self.ui.power_spin.value(),
            "dmx_type": self.ui.dmx_type_combo.currentText(),
            "channels": {},
        }

        # Append channels
        for i, channel in enumerate(self.channels):
            channel_data = channel.channel_data
            fixture_data["channels"][i] = channel_data

        with open(fixture_path, 'w') as f:
            f.write(json.dumps(fixture_data, indent=4))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FixtureEditor()
    window.show()
    sys.exit(app.exec())
