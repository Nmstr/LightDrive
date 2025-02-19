from PySide6.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class SequenceData:
    uuid: str
    name: str
    type: str = field(default="sequence", init=False)
    scenes: list[dict]  # [{"scene_uuid": "---", "entry_uuid": "---", "duration": 500}, ...]

class SequenceAddSceneDialog(QDialog):
    def __init__(self, window) -> None:
        self.window = window
        self.selected_scenes = None
        super().__init__()
        self.setWindowTitle("LightDrive - Add Scene to Sequence")

        layout = QVBoxLayout()
        self.scene_selection_tree = QTreeWidget()
        self.scene_selection_tree.setHeaderHidden(True)
        self.scene_selection_tree.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.scene_selection_tree)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.load_scenes()

    def load_scenes(self) -> None:
        """
        Loads all (non-added) scenes and shows them in the scene_selection_tree
        :return: None
        """
        for snippet_uuid, snippet in self.window.snippet_manager.available_snippets.items():
            if snippet.type != "scene":
                continue

            # Add the scene to the tree
            scene_entry = QTreeWidgetItem()
            scene_entry.uuid = snippet_uuid
            scene_entry.setText(0, snippet.name)
            self.scene_selection_tree.addTopLevelItem(scene_entry)

    def accept(self) -> None:
        """
        Accept the dialog to add the selected scenes to the sequence
        :return:
        """
        self.selected_scenes = self.scene_selection_tree.selectedItems()
        super().accept()

class SequenceManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def sequence_display(self, sequence_uuid: str) -> None:
        """
        Displays the sequence editor
        :param sequence_uuid: The uuid of the sequence to display
        :return: None
        """
        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        self._sequence_load_scenes(sequence_snippet.uuid)

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
            sequence_data = SequenceData(cue_uuid, "New Sequence", scenes=[])
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

    def _sequence_load_scenes(self, sequence_uuid: str) -> None:
        """
        Loads the scenes that are in a sequence specified by the sequence_uuid to the sequence_content_tree
        :param sequence_uuid: The scenes to load
        :return: None
        """
        self.sm.window.ui.sequence_content_tree.clear()

        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        for scene_config in sequence_snippet.scenes:
            scene_entry = QTreeWidgetItem()
            scene_entry.entry_uuid = scene_config["entry_uuid"]
            scene_entry.setText(0, str(sequence_snippet.scenes.index(scene_config) + 1))
            scene_entry.setText(1, f"{scene_config['duration']}ms")
            scene_snippet = self.sm.available_snippets.get(scene_config["scene_uuid"])
            scene_entry.setText(2, scene_snippet.name)
            self.sm.window.ui.sequence_content_tree.addTopLevelItem(scene_entry)

    def sequence_add_scene(self, sequence_uuid: str = None, scene_uuid: str = None):
        if not sequence_uuid:
            sequence_uuid = self.sm.current_snippet.uuid
        dlg = SequenceAddSceneDialog(self.sm.window)
        if not dlg.exec():
            return

        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        for scene_entry in dlg.selected_scenes:
            sequence_snippet.scenes.append({"scene_uuid": scene_entry.uuid, "entry_uuid": str(uuid.uuid4()),"duration": 500})
            self._sequence_load_scenes(sequence_snippet.uuid)

    def sequence_remove_scene(self, sequence_uuid: str = None, entry_uuid: str = None):
        if not sequence_uuid:
            sequence_uuid = self.sm.current_snippet.uuid
        if not entry_uuid:
            entry_uuid = self.sm.window.ui.sequence_content_tree.currentItem().entry_uuid
        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        for scene_config in sequence_snippet.scenes:
            if scene_config["entry_uuid"] == entry_uuid:
                sequence_snippet.scenes.remove(scene_config)
                break
        self._sequence_load_scenes(sequence_snippet.uuid)

    def _sequence_move_shared(self, sequence_uuid: str = None, entry_uuid: str = None) -> tuple | None:
        # Ensure that the sequence_uuid and entry_uuid are set
        if not sequence_uuid:
            sequence_uuid = self.sm.current_snippet.uuid
        if not entry_uuid:
            if not self.sm.window.ui.sequence_content_tree.currentItem():
                return None
            entry_uuid = self.sm.window.ui.sequence_content_tree.currentItem().entry_uuid

        # Find the current entry in the sequence
        sequence_snippet = self.sm.available_snippets.get(sequence_uuid)
        entry = None
        for scene_config in sequence_snippet.scenes:
            if scene_config["entry_uuid"] == entry_uuid:
                entry = scene_config
                break
        if not entry:
            return None
        return sequence_snippet, entry

    def sequence_move_up(self, sequence_uuid: str = None, entry_uuid: str = None) -> None:
        sequence_snippet, entry = self._sequence_move_shared(sequence_uuid, entry_uuid)
        if sequence_snippet is None:
            return  # Either no sequence snippet or entry found

        # Move the entry up in the sequence
        index = sequence_snippet.scenes.index(entry)
        if index == 0:
            return  # Already at the top
        sequence_snippet.scenes.pop(index)
        sequence_snippet.scenes.insert(index - 1, entry)

        # Update the ui
        self._sequence_load_scenes(sequence_snippet.uuid)
        self.sm.window.ui.sequence_content_tree.setCurrentItem(self.sm.window.ui.sequence_content_tree.topLevelItem(index - 1))

    def sequence_move_down(self, sequence_uuid: str = None, entry_uuid: str = None) -> None:
        sequence_snippet, entry = self._sequence_move_shared(sequence_uuid, entry_uuid)

        # Move the entry down in the sequence
        index = sequence_snippet.scenes.index(entry)
        if index == len(sequence_snippet.scenes) - 1:
            return  # Already at the bottom
        sequence_snippet.scenes.pop(index)
        sequence_snippet.scenes.insert(index + 1, entry)

        # Update the ui
        self._sequence_load_scenes(sequence_snippet.uuid)
        self.sm.window.ui.sequence_content_tree.setCurrentItem(self.sm.window.ui.sequence_content_tree.topLevelItem(index + 1))

    def sequence_toggle_show(self):
        print("Show")
