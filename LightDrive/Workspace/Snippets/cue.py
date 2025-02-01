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

    def cue_display(self, cue_uuid: str) -> None:
        """
        Displays the cue editor
        :param cue_uuid: The uuid of the scene to display
        :return: None
        """
        self._load_cue_timeline(cue_uuid)

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

    def cue_rename(self, cue_uuid: str = None, new_name: str = None) -> None:
        """
        Renames the cue with the given UUID to the new name
        :param cue_uuid: The UUID of the cue to rename
        :param new_name: The new name of the cue
        :return: None
        """
        if not cue_uuid:
            cue_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.cue_name_edit.text()
        cue_snippet = self.sm.available_snippets.get(cue_uuid)
        cue_snippet.name = new_name
        cue_entry = self.sm.find_snippet_entry_by_uuid(cue_uuid)
        cue_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def _load_cue_timeline(self, cue_uuid: str) -> None:
        """
        Loads the timeline of the current cue to ui.cue_timeline
        :return: None
        """
        layout = clear_field(self.sm.window.ui.cue_timeline_frame, QVBoxLayout, amount_left = 0)
        cue_snippet = self.sm.available_snippets.get(cue_uuid)
        self.cue_timeline = CueTimeline(self.sm.window, cue_snippet)
        layout.addWidget(self.cue_timeline)

    def cue_add_fixture(self, cue_uuid: str = None) -> None:
        """
        Shows a dialog to add fixtures to the cue specified by the UUID
        :param cue_uuid: The UUID of the cue to add fixtures to (if None, uses the current cue)
        :return: None
        """
        if not cue_uuid:
            cue_uuid = self.sm.current_snippet.uuid
        cue_snippet = self.sm.available_snippets.get(cue_uuid)
        dlg = SnippetAddFixtureDialog(self.sm.window, cue_snippet.fixtures)
        if not dlg.exec():
            return

        for fixture in dlg.selected_fixtures:
            cue_snippet.fixtures.append(fixture.extra_data["fixture_uuid"])
            self._load_cue_timeline(cue_uuid)

    def cue_remove_fixture(self, cue_uuid: str = None, fixture_uuid: str = None) -> None:
        """
        Removes a fixture from the cue
        :param cue_uuid: The UUID of the cue to remove the fixture from (if None, uses the current cue)
        :param fixture_uuid: The UUID of the fixture to remove (if None, aborts)
        :return: None
        """
        if not fixture_uuid:
            return
        if not cue_uuid:
            cue_uuid = self.sm.current_snippet.uuid
        cue_snippet = self.sm.available_snippets.get(cue_uuid)
        cue_snippet.fixtures.remove(fixture_uuid)
        self._load_cue_timeline(cue_uuid)

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
