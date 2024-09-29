from channel_entry import ChannelEntry
from PySide6.QtWidgets import QApplication, QMainWindow
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

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("FixtureEditor")
        self.setWindowTitle("LightDrive")
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

        self.ui.add_channel_btn.clicked.connect(self.add_channel)
        self.ui.open_btn.clicked.connect(self.open_fixture)
        self.ui.save_btn.clicked.connect(self.save_fixture)

    def add_channel(self) -> None:
        """
        Add a channel to the fixture
        :return: None
        """
        layout = self.ui.channel_container.layout()
        channel_entry = ChannelEntry()
        layout.insertWidget(layout.count() - 1, channel_entry)
        self.channels.append(channel_entry)

    def open_fixture(self) -> None:
        """
        Open a fixture
        :return: None
        """

    def save_fixture(self) -> None:
        """
        Save the current fixture
        :return: None
        """
        # Check if fixture can be saved
        fixture_name = self.ui.name_edit.text()
        print(fixture_name)
        if fixture_name == "":
            print("Invalid name")
            return
        if not is_alphanumeric_with_spaces(fixture_name):
            print("Invalid name")
            return
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        fixture_path = os.path.join(fixture_dir, f"{fixture_name}.json")
        if os.path.exists(fixture_path) and self.file_path != fixture_path:
            print("Invalid name")
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
                print("All channels need to be named")
                return
            fixture_data["channels"][i] = channel_data

        with open(fixture_path, 'w') as f:
            f.write(json.dumps(fixture_data, indent=4))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
