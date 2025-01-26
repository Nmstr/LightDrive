from Workspace.Dialogs.snippet_dialogs import SnippetAddFixtureDialog
from Workspace.Widgets.cue_timeline import CueTimeline
from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class CueData:
    uuid: str
    name: str
    type: str = field(default="cue", init=False)
    fixtures: list
    keyframes: dict

class CueManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def cue_create(self, *, parent: QTreeWidgetItem = None, cue_data: CueData = None) -> None:
        """
        Creates a cue in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param cue_data: The data of the cue (only if importing)
        :return: None
        """
        cue_entry = QTreeWidgetItem()
        cue_entry.setIcon(0, QPixmap("Assets/Icons/cue.svg"))
        if not cue_data:
            cue_uuid = str(uuid.uuid4())
            cue_data = CueData(cue_uuid, "New Cue", fixtures=[], keyframes={})
        cue_entry.uuid = cue_data.uuid
        self.sm.available_snippets[cue_data.uuid] = cue_data

        cue_entry.setText(0, self.sm.available_snippets[cue_data.uuid].name)
        self.sm.add_item(cue_entry, parent)

    def cue_rename(self) -> None:
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
        self.cue_timeline.play()

    def cue_pause(self) -> None:
        """
        Pauses the cue
        :return: None
        """
        self.cue_timeline.pause()

    def cue_stop(self) -> None:
        """
        Stops the cue
        :return: None
        """
        self.cue_timeline.stop()
