from PySide6.QtWidgets import QDialog, QVBoxLayout, QTreeWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import json
import os

class SnippetAddFixtureDialog(QDialog):
    def __init__(self, window, added_fixtures) -> None:
        self.window = window
        self.added_fixtures = added_fixtures
        self.selected_fixtures = None
        super().__init__()
        self.setObjectName("SnippetAddFixtureDialog")
        self.setWindowTitle("LightDrive - Scene Add Fixture")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/snippet_add_fixture_dialog.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)
        self.ui.fixture_selection_tree.itemDoubleClicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        self.load_fixtures()

    def load_fixtures(self) -> None:
        """
        Loads the fixtures and shows them in the fixture_selection_tree
        :return: None
        """
        for fixture in self.window.available_fixtures:
            if fixture.get("fixture_uuid") in self.added_fixtures:
                continue  # Don't show fixtures that are already added

            # Load fixture data
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture["id"] + ".json"), 'r') as f:
                fixture_data = json.load(f)

            # Add the item
            fixture_item = QTreeWidgetItem()
            fixture_item.extra_data = fixture
            fixture_item.setText(0, fixture["name"])
            fixture_item.setText(1, f"{fixture['universe']}>{fixture['address']}-{fixture['address'] + len(fixture_data["channels"]) - 1}")
            fixture_item.setText(2, fixture["id"])
            fixture_item.setText(3, fixture["fixture_uuid"])
            self.ui.fixture_selection_tree.addTopLevelItem(fixture_item)

    def accept(self) -> None:
        """
        Accept the dialog to add the selected fixtures
        :return:
        """
        self.selected_fixtures = self.ui.fixture_selection_tree.selectedItems()
        super().accept()
