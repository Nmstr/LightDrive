from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class DirectoryData:
    uuid: str
    name: str
    type: str = field(default="directory", init=False)

class DirectoryManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def dir_create(self, *, parent: QTreeWidgetItem = None, directory_data: DirectoryData = None) -> QTreeWidgetItem:
        """
        Creates a directory in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param directory_data: The data of the directory (only if importing)
        :return: The created directory item
        """
        dir_entry = QTreeWidgetItem()
        dir_entry.setIcon(0, QPixmap("Assets/Icons/directory.svg"))
        if not directory_data:
            dir_uuid = str(uuid.uuid4())
            directory_data = DirectoryData(dir_uuid, "New Directory")
        dir_entry.uuid = directory_data.uuid
        dir_entry.setData(0, Qt.UserRole, "directory")
        self.sm.available_snippets[directory_data.uuid] = directory_data

        dir_entry.setText(0, self.sm.available_snippets[directory_data.uuid].name)
        self.sm.add_item(dir_entry, parent)
        return dir_entry

    def dir_rename(self, dir_uuid: str = None, new_name: str = None) -> None:
        """
        Renames a directory with the given uuid to the new name
        :param dir_uuid: The uuid of the directory to rename (if None, uses the currently selected snippets uuid)
        :param new_name: The new name of the directory (if None, uses the name from ui.directory_name_edit)
        :return: None
        """
        if not dir_uuid:
            dir_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.directory_name_edit.text()
        dir_snippet = self.sm.available_snippets.get(dir_uuid)
        dir_snippet.name = new_name
        dir_entry = self.sm.find_snippet_entry_by_uuid(dir_uuid)
        dir_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
