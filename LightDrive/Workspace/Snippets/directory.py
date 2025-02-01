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
        self.sm.available_snippets[directory_data.uuid] = directory_data

        dir_entry.setText(0, self.sm.available_snippets[directory_data.uuid].name)
        self.sm.add_item(dir_entry, parent)
        return dir_entry

    def dir_rename(self) -> None:
        """
        Renames the directory to the new name
        :return: None
        """
        self.sm.current_snippet.name = self.sm.window.ui.directory_name_edit.text()
        dir_entry = self.sm.find_snippet_entry_by_uuid(self.sm.current_snippet.uuid)
        dir_entry.setText(0, self.sm.current_snippet.name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
