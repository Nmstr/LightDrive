from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class SoundResourceData:
    uuid: str
    name: str
    type: str = field(default="sound_resource", init=False)
    directory: str = field(default="root")

class SoundResourceManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def sound_resource_display(self, sound_resource_uuid: str) -> None:
        """
        Displays the sound resource editor for the given sound resource uuid
        :param sound_resource_uuid: The uuid of the sound resource to display
        :return: None
        """
        print(sound_resource_uuid)

    def sound_resource_create(self, *, parent: QTreeWidgetItem = None, sound_resource_data: SoundResourceData = None) -> None:
        """
        Creates a sound resource in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param sound_resource_data: The data of the sound resource (only if importing)
        :return: None
        """
        sound_resource_entry = QTreeWidgetItem()
        sound_resource_entry.setIcon(0, QPixmap("Assets/Icons/sound_resource.svg"))
        if not sound_resource_data:
            sound_resource_uuid = str(uuid.uuid4())
            sound_resource_data = SoundResourceData(sound_resource_uuid, "New Sound Resource")
        sound_resource_entry.uuid = sound_resource_data.uuid
        self.sm.available_snippets[sound_resource_data.uuid] = sound_resource_data

        sound_resource_entry.setText(0, self.sm.available_snippets[sound_resource_data.uuid].name)
        self.sm.add_item(sound_resource_entry, parent)

    def sound_resource_rename(self, sound_resource_uuid: str = None, new_name: str = None) -> None:
        """
        Renames a sound_resource with the given uuid to the new name
        :param sound_resource_uuid: The uuid of the sound_resource to rename (if None, uses the currently selected snippets uuid)
        :param new_name: The new name of the sound_resource (if None, uses the name from ui.sound_resource_name_edit)
        :return: None
        """
        if not sound_resource_uuid:
            sound_resource_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.sound_resource_name_edit.text()
        sound_resource_snippet = self.sm.available_snippets.get(sound_resource_uuid)
        sound_resource_snippet.name = new_name
        sound_resource_entry = self.sm.find_snippet_entry_by_uuid(sound_resource_uuid)
        sound_resource_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
