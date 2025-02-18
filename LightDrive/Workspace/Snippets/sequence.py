from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class SequenceData:
    uuid: str
    name: str
    type: str = field(default="sequence", init=False)
    scenes: dict  # e.g.: {scene_uuid: {"duration": 5}}

class SequenceManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def sequence_display(self, sequence_uuid: str) -> None:
        """
        Displays the sequence editor
        :param sequence_uuid: The uuid of the sequence to display
        :return: None
        """
        print(sequence_uuid)

    def sequence_create(self, *, parent: QTreeWidgetItem = None, sequence_data: SequenceData = None) -> None:
        """
        Creates a sequence in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param sequence_data: The data of the sequence (only if importing)
        :return: None
        """
        sequence_entry = QTreeWidgetItem()
        sequence_entry.setIcon(0, QPixmap("Assets/Icons/sequence.svg"))
        if not sequence_data:
            cue_uuid = str(uuid.uuid4())
            sequence_data = SequenceData(cue_uuid, "New Sequence", scenes={})
        sequence_entry.uuid = sequence_data.uuid
        self.sm.available_snippets[sequence_data.uuid] = sequence_data

        sequence_entry.setText(0, self.sm.available_snippets[sequence_data.uuid].name)
        self.sm.add_item(sequence_entry, parent)

    def sequence_rename(self, sequence_uuid: str = None, new_name: str = None) -> None:
        """
        Renames the sequence with the given UUID to the new name
        :param sequence_uuid: The UUID of the sequence to rename
        :param new_name: The new name of the sequence
        :return: None
        """
        if not sequence_uuid:
            sequence_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.sequence_name_edit.text()
        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        sequence_snippet.name = new_name
        sequence_entry = self.sm.find_snippet_entry_by_uuid(sequence_uuid)
        sequence_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def sequence_add_scene(self, sequence_uuid = None, scene_uuid = None):
        print("Add Scene", sequence_uuid, scene_uuid)

    def sequence_remove_scene(self, sequence_uuid = None, scene_uuid = None):
        print("Remove Scene", sequence_uuid, scene_uuid)

    def sequence_toggle_show(self):
        print("Show")
