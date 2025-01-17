from PySide6.QtWidgets import QDialog, QVBoxLayout, QTreeWidgetItem, QListWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
import json
import os

class AddFixtureDialog(QDialog):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        self.current_selected_fixture_item = None
        self.channel_data = None
        self.setWindowTitle("LightDrive - Add Fixture")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/add_fixture_dialog.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        self.ui.fixture_selection_tree.itemClicked.connect(self.select_fixture)
        self.ui.fixture_selection_tree.itemDoubleClicked.connect(self.accept_fixture)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        self.load_universes()
        self.load_fixtures()

    def load_universes(self):
        for universe_uuid, universe_data in self.window.dmx_output.get_configuration().items():
            self.ui.universe_combo.addItem(universe_data["name"], universe_uuid)

    def load_fixtures(self) -> None:
        """
        Loads the fixtures and shows them in the fixture_selection_tree
        :return: None
        """
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        for fixture in os.listdir(fixture_dir):
            with open(os.path.join(fixture_dir, fixture), 'r') as f:
                fixture_data = json.load(f)

            # Check if manufacturer entry already exists, and if not create it
            manufacturer_item = self.ui.fixture_selection_tree.findItems(fixture_data["manufacturer"], Qt.MatchExactly)
            if manufacturer_item:
                manufacturer_item = manufacturer_item[0]  # Replace the one item list with just the item
            else:
                manufacturer_item = QTreeWidgetItem()
                manufacturer_item.setText(0, fixture_data["manufacturer"])
                self.ui.fixture_selection_tree.addTopLevelItem(manufacturer_item)

            # Add the item
            fixture_item = QTreeWidgetItem(manufacturer_item)
            fixture_item.extra_data = fixture_data
            fixture_item.setText(0, fixture_data["name"])

    def select_fixture(self, item: QTreeWidgetItem) -> None:
        """
        Selects the clicked fixture from the fixture_selection_tree
        :param item: The QTreeWidgetItem that was clicked
        :return: None
        """
        if item.childCount() != 0:  # Disregard top level items (manufacturers)
            return
        self.current_selected_fixture_item = item
        self.ui.name_edit.setText(item.text(0))

        # Fill channel_list with all channels
        fixture_data = self.current_selected_fixture_item.extra_data
        self.ui.channel_list.clear()
        for key, value in fixture_data["channels"].items():
            channel_entry = QListWidgetItem(f"{key}: {value['name']}")
            channel_entry.setIcon(QPixmap(f"Assets/Icons/{value["type"].lower()}.svg"))
            self.ui.channel_list.addItem(channel_entry)

    def accept_fixture(self, item: QTreeWidgetItem) -> None:
        """
        Accepts the double-clicked fixture from the fixture_selection_tree
        :param item: The QTreeWidgetItem that was clicked
        :return: None
        """
        if item.childCount() != 0:  # Disregard top level items (manufacturers)
            return
        self.current_selected_fixture_item = item
        super().accept()
        
    def accept(self):
        super().accept()
