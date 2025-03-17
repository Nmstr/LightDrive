from Backend.output import OutputSnippet
from Workspace.Dialogs.snippet_dialogs import SnippetAddFixtureDialog
from Workspace.Widgets.value_slider import SceneSlider
from PySide6.QtWidgets import QTreeWidgetItem, QListWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, \
    QSizePolicy, QScrollArea, QPushButton, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid
import json
import copy
import os

@dataclass
class SceneData:
    uuid: str
    name: str
    type: str = field(default="scene", init=False)
    fixtures: list
    fixture_configs: dict
    directory: str = field(default="root")

class SceneFixtureConfigScreen(QWidget):
    def __init__(self, parent=None, fixture_data=None, snippet_manager=None):
        self.window = parent
        self.fixture_data = fixture_data
        self.sm = snippet_manager
        super().__init__(parent)
        self.clipboard = None

        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.btn_frame = QFrame()
        self.btn_frame.setLayout(btn_layout)
        layout.addWidget(self.btn_frame)

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setIcon(QPixmap("Assets/Icons/copy.svg"))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)
        self.paste_btn = QPushButton("Paste")
        self.paste_btn.setIcon(QPixmap("Assets/Icons/paste.svg"))
        self.paste_btn.clicked.connect(self.paste_clipboard)
        btn_layout.addWidget(self.paste_btn)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.scroll_widget = QWidget()
        self.scroll.setWidget(self.scroll_widget)

        scroll_layout = QHBoxLayout()
        self.scroll_widget.setLayout(scroll_layout)

        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture_data["id"] + ".json")) as f:
            amount_channels = len(json.load(f)["channels"])  # Get the amount of channels
        self.sliders = []
        for i in range(amount_channels):
            scene_snippet = self.sm.available_snippets.get(self.sm.current_snippet.uuid)
            self.sliders.append(SceneSlider(self.window, i, fixture_data, scene_snippet))
            scroll_layout.addWidget(self.sliders[i])

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_layout.addItem(self.spacer)

        self.setLayout(layout)

    def copy_to_clipboard(self) -> None:
        """
        Copy the dmx values, that the current fixture in the scene is configured to, to the clipboard.
        :return: None
        """
        scene_config = copy.deepcopy(self.sm.current_snippet.fixture_configs)
        fixture_config = {
            "type": "scene",
            "data": scene_config.get(self.fixture_data["fixture_uuid"])
        }
        self.sm.clipboard = fixture_config

    def paste_clipboard(self):
        """
        Pastes the dmx values, that are currently in the clipboard, to the currently selected fixture in the scene.
        :return: None
        """
        clipboard_data = self.sm.clipboard
        if not isinstance(clipboard_data, dict):
            return  # The clipboard is empty or contains invalid data
        match clipboard_data.get("type"):
            case "scene":
                for channel_num, channel_data in clipboard_data.get("data", {}).items():
                    self.sliders[int(channel_num)].set_value(channel_data.get("value", 0))
                    self.sliders[int(channel_num)].set_activated(channel_data.get("checked", False))

class SceneManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager
        self.clipboard = None

    def scene_display(self, scene_uuid: str) -> None:
        """
        Displays the scene editor
        :param scene_uuid: The uuid of the scene to display
        :return: None
        """
        scene_snippet = self.sm.available_snippets.get(scene_uuid)
        self._scene_load_fixtures(scene_snippet.fixtures)

    def scene_create(self, *, parent: QTreeWidgetItem = None, scene_data: SceneData = None) -> None:
        """
        Creates a scene in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param scene_data: The data of the scene (only if importing)
        :return: None
        """
        scene_entry = QTreeWidgetItem()
        scene_entry.setIcon(0, QPixmap("Assets/Icons/scene.svg"))
        if not scene_data:
            scene_uuid = str(uuid.uuid4())
            scene_data = SceneData(scene_uuid, "New Scene", fixtures=[], fixture_configs={})
        scene_entry.uuid = scene_data.uuid
        self.sm.available_snippets[scene_data.uuid] = scene_data

        scene_entry.setText(0, self.sm.available_snippets[scene_data.uuid].name)
        self.sm.add_item(scene_entry, parent)

    def scene_rename(self, scene_uuid: str = None, new_name: str = None) -> None:
        """
        Renames a scene with the given uuid to the new name
        :param scene_uuid: The uuid of the scene to rename (if None, uses the currently selected snippets uuid)
        :param new_name: The new name of the scene (if None, uses the name from ui.scene_name_edit)
        :return: None
        """
        if not scene_uuid:
            scene_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.scene_name_edit.text()
        scene_snippet = self.sm.available_snippets.get(scene_uuid)
        scene_snippet.name = new_name
        scene_entry = self.sm.find_snippet_entry_by_uuid(scene_uuid)
        scene_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def _scene_load_fixtures(self, fixture_ids: dict) -> None:
        """
        Loads the fixtures that are in a scene to ui.scene_fixture_list
        :param fixture_ids: The ids of the fixtures to load
        :return: None
        """
        self.sm.window.ui.scene_fixture_list.clear()  # First remove all the fixtures from the QListWidget
        for i in reversed(range(self.sm.window.ui.scene_config_tab.count() - 1)):
            self.sm.window.ui.scene_config_tab.removeTab(i + 1)

        scene_fixtures = []
        for fixture_uuid in fixture_ids:  # Get the data from all the fixtures in the scene
            matching_fixture = [item for item in self.sm.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0]
            scene_fixtures.append(matching_fixture)
        for fixture in scene_fixtures:  # Add the fixture to the QListWidget
            fixture_item = QListWidgetItem(fixture["name"])
            fixture_item.extra_data = fixture
            self.sm.window.ui.scene_fixture_list.addItem(fixture_item)
            self._scene_load_fixture_tab(fixture)

    def _scene_load_fixture_tab(self, fixture_data: dict) -> None:
        """
        Creates the tab to configure a fixture
        :param fixture_data: The data of the fixture
        :return: None
        """
        self.sm.window.ui.scene_config_tab.addTab(SceneFixtureConfigScreen(self.sm.window, fixture_data, self.sm), fixture_data["name"])

    def scene_add_fixture(self, scene_uuid: str = None) -> None:
        """
        Shows a dialog to add fixtures to the scene+ui.scene_fixture_list and adds them to the scene specified by uuid if successful
        :param scene_uuid: The uuid of the scene to add the fixtures to
        :return: None
        """
        if not scene_uuid:
            scene_uuid = self.sm.current_snippet.uuid
        scene_snippet = self.sm.available_snippets.get(scene_uuid)
        print(scene_snippet)
        dlg = SnippetAddFixtureDialog(self.sm.window, scene_snippet.fixtures)
        if not dlg.exec():
            return

        for fixture in dlg.selected_fixtures:
            scene_snippet.fixtures.append(fixture.extra_data["fixture_uuid"])
            self._scene_load_fixtures(scene_snippet.fixtures)

    def scene_remove_fixture(self, scene_uuid: str = None, fixture_uuid: str = None) -> None:
        """
        Removes a fixture from the scene.ui.scene_fixture_list
        :return: None
        """
        if not scene_uuid:
            scene_uuid = self.sm.current_snippet.uuid
        if not fixture_uuid:
            fixture_uuid = self.sm.window.ui.scene_fixture_list.selectedItems()[0].extra_data["fixture_uuid"]
        scene_snippet = self.sm.available_snippets.get(scene_uuid)
        scene_snippet.fixtures.remove(fixture_uuid)
        self._scene_load_fixtures(scene_snippet.fixtures)

    def scene_construct_output_values(self, snippet_uuid: str) -> dict:
        """
        Constructs output values for a scene with a specific UUID
        :param snippet_uuid: The uuid of the scene
        :return: The output values
        """
        output_values = {}
        fixture_configs = self.sm.available_snippets.get(snippet_uuid).fixture_configs
        available_fixtures = self.sm.window.available_fixtures

        for fixture_uuid, channels in fixture_configs.items():
            fixture = next((f for f in available_fixtures if f["fixture_uuid"] == fixture_uuid), None)
            if not fixture:
                continue

            universe = fixture["universe"]
            address = fixture["address"]

            if universe not in output_values:
                output_values[universe] = {}

            for channel_offset, channel_data in channels.items():
                if not channel_data.get("checked"):
                    continue
                channel = address + int(channel_offset)
                output_values[universe][channel] = channel_data["value"]

        return output_values

    def scene_toggle_show(self) -> None:
        """
        Toggles whether the scene is being outputted over dmx or not
        :return: None
        """
        if self.sm.current_display_snippet is not None:  # Remove the current display snippet if it exists
            self.sm.window.dmx_output.remove_snippet(self.sm.current_display_snippet)
            self.sm.current_display_snippet = None

        if self.sm.window.ui.scene_show_btn.isChecked():  # Add the new snippet if necessary
            output_values = self.scene_construct_output_values(self.sm.current_snippet.uuid)
            if not output_values:
                return
            self.sm.current_display_snippet = OutputSnippet(self.sm.window.dmx_output, output_values)
            self.sm.window.dmx_output.insert_snippet(self.sm.current_display_snippet)
