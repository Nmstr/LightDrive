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

class SceneFixtureConfigScreen(QWidget):
    def __init__(self, parent=None, fixture_data=None):
        self.window = parent
        self.fixture_data = fixture_data
        super().__init__(parent)

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
            self.sliders.append(SceneSlider(self.window, i, fixture_data))
            scroll_layout.addWidget(self.sliders[i])

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_layout.addItem(self.spacer)

        self.setLayout(layout)

    def copy_to_clipboard(self) -> None:
        """
        Copy the dmx values, that the current fixture in the scene is configured to, to the clipboard.
        :return: None
        """
        scene_config = copy.deepcopy(self.window.snippet_manager.current_snippet.extra_data.get("fixture_configs"))
        fixture_config = {
            "type": self.window.snippet_manager.current_snippet.extra_data.get("type"),
            "data": scene_config.get(self.fixture_data["fixture_uuid"])
        }
        self.window.snippet_manager.clipboard = fixture_config

    def paste_clipboard(self):
        """
        Pastes the dmx values, that are currently in the clipboard, to the currently selected fixture in the scene.
        :return: None
        """
        clipboard_data = self.window.snippet_manager.clipboard
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

    def scene_rename(self) -> None:
        """
        Changes the name of the current scene to a new name from ui.scene_name_edit
        :return: None
        """
        self.current_snippet.extra_data["name"] = self.window.ui.scene_name_edit.text()
        self.current_snippet.setText(0, self.window.ui.scene_name_edit.text())
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def _scene_load_fixtures(self, fixture_ids: dict) -> None:
        """
        Loads the fixtures that are in a scene to ui.scene_fixture_list
        :param fixture_ids: The ids of the fixtures to load
        :return: None
        """
        self.window.ui.scene_fixture_list.clear()  # First delete old data
        for i in reversed(range(self.window.ui.scene_config_tab.count() - 1)):
            self.window.ui.scene_config_tab.removeTab(i + 1)

        scene_fixtures = []
        for fixture_uuid in fixture_ids:  # Get the data from all the fixtures in the scene
            matching_fixture = [item for item in self.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0]
            scene_fixtures.append(matching_fixture)
        for fixture in scene_fixtures:  # Add the fixture to the QListWidget
            fixture_item = QListWidgetItem(fixture["name"])
            fixture_item.extra_data = fixture
            self.window.ui.scene_fixture_list.addItem(fixture_item)
            self._scene_load_fixture_tab(fixture)

    def _scene_load_fixture_tab(self, fixture_data: dict) -> None:
        """
        Creates the tab to configure a fixture
        :param fixture_data: The data of the fixture
        :return: None
        """
        self.window.ui.scene_config_tab.addTab(SceneFixtureConfigScreen(self.window, fixture_data), fixture_data["name"])

    def scene_add_fixture(self) -> None:
        """
        Shows a dialog to add fixtures to the scene+ui.scene_fixture_list and adds them if successful
        :return: None
        """
        dlg = SnippetAddFixtureDialog(self.window, self.current_snippet.extra_data.get("fixtures", []))
        if not dlg.exec():
            return

        if not self.current_snippet.extra_data.get("fixtures"):  # Add fixtures to extra_data if it doesn't exist
            self.current_snippet.extra_data["fixtures"] = []
        for fixture in dlg.selected_fixtures:
            self.current_snippet.extra_data["fixtures"].append(fixture.extra_data["fixture_uuid"])
            self._scene_load_fixtures(self.current_snippet.extra_data.get("fixtures", []))

    def scene_remove_fixture(self) -> None:
        """
        Removes a fixture from the scene+ui.scene_fixture_list
        :return: None
        """
        selected_uuid = self.window.ui.scene_fixture_list.selectedItems()[0].extra_data["fixture_uuid"]
        self.current_snippet.extra_data["fixtures"].remove(selected_uuid)
        self._scene_load_fixtures(self.current_snippet.extra_data.get("fixtures", []))

    def scene_construct_output_values(self, snippet_uuid: str) -> dict:
        """
        Constructs output values for a scene with a specific UUID
        :param snippet_uuid: The uuid of the scene
        :return: The output values
        """
        output_values = {}

        fixture_configs = self.find_snippet_by_uuid(snippet_uuid).get("fixture_configs", {})
        available_fixtures = self.window.available_fixtures

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
        if self.current_display_snippet is not None:  # Remove the current display snippet if it exists
            self.window.dmx_output.remove_snippet(self.current_display_snippet)
            self.current_display_snippet = None

        if self.window.ui.scene_show_btn.isChecked():  # Add the new snippet if necessary
            output_values = self.scene_construct_output_values(self.current_snippet.extra_data.get("uuid"))
            if not output_values:
                return
            self.current_display_snippet = OutputSnippet(self.window.dmx_output, output_values)
            self.window.dmx_output.insert_snippet(self.current_display_snippet)
