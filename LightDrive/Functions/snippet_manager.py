from Workspace.Dialogs.snippet_dialogs import SnippetAddFixtureDialog
from Workspace.Widgets.value_slider import SceneSlider
from Workspace.Widgets.cue_timeline import CueTimeline
from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QListWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, \
    QSizePolicy, QScrollArea, QPushButton, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import uuid
import json
import copy
import os

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

class SnippetManager:
    def __init__(self, window = None):
        """
        Creates the snippet manager
        :param window: The application's main window
        """
        self.current_snippet = None
        self.clipboard = None
        self.window = window

    def create_cue(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a cue in the snippet selector tree
        :param extra_data: Any extra data for the cue (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_cue = QTreeWidgetItem()
        new_cue.setIcon(0, QPixmap("Assets/Icons/cue.svg"))
        if extra_data:
            new_cue.extra_data = extra_data
        else:
            new_cue.extra_data = {
                "type": "cue",
                "uuid": str(uuid.uuid4()),
                "name": "New Cue",
            }
        new_cue.setText(0, new_cue.extra_data["name"])
        self._add_item(new_cue, parent)

    def create_scene(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a scene in the snippet selector tree
        :param extra_data: Any extra data for the scene (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_scene = QTreeWidgetItem()
        new_scene.setIcon(0, QPixmap("Assets/Icons/scene.svg"))
        if extra_data:
            new_scene.extra_data = extra_data
        else:
            new_scene.extra_data = {
                "type": "scene",
                "uuid": str(uuid.uuid4()),
                "name": "New Scene",
                "fixtures": [],
                "fixture_configs": {}
            }
        new_scene.setText(0, new_scene.extra_data["name"])
        self._add_item(new_scene, parent)

    def create_efx_2d(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a 2d efx in the snippet selector tree
        :param extra_data: Any extra data for the 2d efx (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_efx_2d = QTreeWidgetItem()
        new_efx_2d.setIcon(0, QPixmap("Assets/Icons/efx_2d.svg"))
        if extra_data:
            new_efx_2d.extra_data = extra_data
        else:
            new_efx_2d.extra_data = {
                "type": "efx_2d",
                "uuid": str(uuid.uuid4()),
                "name": "New 2D EFX",
            }
        new_efx_2d.setText(0, new_efx_2d.extra_data["name"])
        self._add_item(new_efx_2d, parent)

    def create_rgb_matrix(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a rgb matrix in the snippet selector tree
        :param extra_data: Any extra data for the rgb matrix (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_rgb_matrix = QTreeWidgetItem()
        new_rgb_matrix.setIcon(0, QPixmap("Assets/Icons/rgb_matrix.svg"))
        if extra_data:
            new_rgb_matrix.extra_data = extra_data
        else:
            new_rgb_matrix.extra_data = {
                "type": "rgb_matrix",
                "uuid": str(uuid.uuid4()),
                "name": "New RGB Matrix",
            }
        new_rgb_matrix.setText(0, new_rgb_matrix.extra_data["name"])
        self._add_item(new_rgb_matrix, parent)

    def create_script(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a script in the snippet selector tree
        :param extra_data: Any extra data for the script (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_script = QTreeWidgetItem()
        new_script.setIcon(0, QPixmap("Assets/Icons/script.svg"))
        if extra_data:
            new_script.extra_data = extra_data
        else:
            new_script.extra_data = {
                "type": "script",
                "uuid": str(uuid.uuid4()),
                "name": "New Script",
            }
        new_script.setText(0, new_script.extra_data["name"])
        self._add_item(new_script, parent)

    def create_dir(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> QTreeWidgetItem:
        """
        Creates a directory in the snippet selector tree
        :param extra_data: Any extra data for the directory (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: The created directory item
        """
        new_dir = QTreeWidgetItem()
        new_dir.setIcon(0, QPixmap("Assets/Icons/directory.svg"))
        if extra_data:
            new_dir.extra_data = extra_data
        else:
            new_dir.extra_data = {
                "type": "directory",
                "uuid": str(uuid.uuid4()),
                "name": "New Directory",
            }
        new_dir.setText(0, new_dir.extra_data["name"])
        self._add_item(new_dir, parent)
        return new_dir

    def _add_item(self, item: QTreeWidgetItem, parent: QTreeWidgetItem = None) -> None:
        """
        Adds the provided item to the snippet selector tree
        :param item: The item to add
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        selector_tree = self.window.ui.snippet_selector_tree
        if parent:  # Used for importing snippets
            parent.addChild(item)
            parent.setExpanded(True)
            return
        if selector_tree.selectedItems() and selector_tree.selectedItems()[0].extra_data["type"] == "directory":
            selector_tree.selectedItems()[0].addChild(item)
            selector_tree.selectedItems()[0].setExpanded(True)
        else:
            selector_tree.addTopLevelItem(item)
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def show_editor(self, item) -> None:
        """
        Shows the snippet editor for the selected snippet
        :param item: The snippet to edit
        :return: None
        """
        self.current_snippet = item
        match self.current_snippet.extra_data["type"]:
            case "directory":
                self.window.ui.snippet_editor.setCurrentIndex(1)
                self.window.ui.directory_name_edit.setText(self.current_snippet.extra_data["name"])
            case "cue":
                self.window.ui.snippet_editor.setCurrentIndex(2)
                self.window.ui.cue_name_edit.setText(self.current_snippet.extra_data["name"])
                self._load_cue_timeline()
            case "scene":
                self.window.ui.snippet_editor.setCurrentIndex(6)
                self.window.ui.scene_name_edit.setText(self.current_snippet.extra_data["name"])
                self._scene_load_fixtures(self.current_snippet.extra_data.get("fixtures", []))
            case "efx_2d":
                self.window.ui.snippet_editor.setCurrentIndex(3)
            case "rgb_matrix":
                self.window.ui.snippet_editor.setCurrentIndex(4)
            case "script":
                self.window.ui.snippet_editor.setCurrentIndex(5)

    def rename_scene(self) -> None:
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

    def rename_cue(self) -> None:
        """
        Changes the name of the current cue to a new name from ui.cue_name_edit
        :return: None
        """
        self.current_snippet.extra_data["name"] = self.window.ui.cue_name_edit.text()
        self.current_snippet.setText(0, self.window.ui.cue_name_edit.text())
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def _load_cue_timeline(self) -> None:
        """
        Loads the timeline of the current cue to ui.cue_timeline
        :return: None
        """
        layout = clear_field(self.window.ui.cue_timeline_frame, QVBoxLayout, amount_left = 0)
        self.cue_timeline = CueTimeline(self.window, self.current_snippet.extra_data.get("fixtures", []))
        layout.addWidget(self.cue_timeline)

    def cue_add_fixture(self) -> None:
        """
        Shows a dialog to add fixtures to the cue
        :return: None
        """
        dlg = SnippetAddFixtureDialog(self.window, self.current_snippet.extra_data.get("fixtures", []))
        if not dlg.exec():
            return

        if not self.current_snippet.extra_data.get("fixtures"):  # Add fixtures to extra_data if it doesn't exist
            self.current_snippet.extra_data["fixtures"] = []
        for fixture in dlg.selected_fixtures:
            self.current_snippet.extra_data["fixtures"].append(fixture.extra_data["fixture_uuid"])
            self._load_cue_timeline()

    def cue_remove_fixture(self, fixture_uuid) -> None:
        """
        Removes a fixture from the cue
        :param fixture_uuid: The UUID of the fixture to remove
        :return: None
        """
        self.current_snippet.extra_data["fixtures"].remove(fixture_uuid)
        self._load_cue_timeline()

    def cue_play(self) -> None:
        """
        Plays the cue
        :return: None
        """
        pass

    def cue_pause(self) -> None:
        """
        Pauses the cue
        :return: None
        """
        pass

    def cue_stop(self) -> None:
        """
        Stops the cue
        :return: None
        """
        pass

    def rename_dir(self) -> None:
        """
        Renames the directory to the new name
        :return: None
        """
        self.current_snippet.extra_data["name"] = self.window.ui.directory_name_edit.text()
        self.current_snippet.setText(0, self.window.ui.directory_name_edit.text())
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
