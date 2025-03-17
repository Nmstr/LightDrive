from PySide6.QtWidgets import QTreeWidgetItem, QDialog, QVBoxLayout, QTreeWidget, QDialogButtonBox, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

class DirectoryAddChildrenDialog(QDialog):
    def __init__(self, window) -> None:
        """
        Create a dialog for selecting children of directory
        :param window: The main window
        """
        super().__init__()
        self.setWindowTitle("LightDrive - Add Children to Directory")
        self.window = window

        layout = QVBoxLayout()
        self.snippet_tree = QTreeWidget()
        self.snippet_tree.setHeaderHidden(True)
        self.load_snippets()
        layout.addWidget(self.snippet_tree)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def load_snippets(self) -> None:
        """
        Loads the snippets and shows them in the snippet_tree
        :return: None
        """
        def add_items(source_item, target_parent):
            for i in range(source_item.childCount()):
                child = source_item.child(i)
                new_item = QTreeWidgetItem(target_parent)
                new_item.setText(0, child.text(0))
                new_item.snippet_uuid = child.uuid
                add_items(child, new_item)

        root = self.window.ui.snippet_selector_tree.invisibleRootItem()
        add_items(root, self.snippet_tree)

@dataclass
class DirectoryData:
    uuid: str
    name: str
    type: str = field(default="directory", init=False)
    directory: str = field(default="root")

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

    def dir_add_children(self, dir_uuid: str = None) -> None:
        """
        Adds snippets as children to the given directory
        :param dir_uuid: The uuid of the directory to add a child to (if None, uses the currently selected snippets uuid)
        :return: None
        """
        if not dir_uuid:  # If no directory is given, use the currently selected snippet
            dir_uuid = self.sm.current_snippet.uuid
        dir_entry = self.sm.find_snippet_entry_by_uuid(dir_uuid)
        # Open the dialog for selecting snippets
        add_children_dialog = DirectoryAddChildrenDialog(self.sm.window)
        if add_children_dialog.exec():
            selected_items = add_children_dialog.snippet_tree.selectedItems()
            for item in selected_items:  # Iterate over all selected items
                if item.snippet_uuid == dir_uuid:  # Prevent adding the directory to itself
                    err_msg = QMessageBox()
                    err_msg.setText("Directories cannot be added to themselves")
                    err_msg.exec()
                    continue
                snippet_entry = self.sm.find_snippet_entry_by_uuid(item.snippet_uuid)
                if snippet_entry.parent():  # If the snippet is already a child of a directory, remove it from there
                    snippet_entry.parent().removeChild(snippet_entry)
                else:  # If the snippet is not a child of a directory, remove it from the root
                    self.sm.window.ui.snippet_selector_tree.takeTopLevelItem(self.sm.window.ui.snippet_selector_tree.indexOfTopLevelItem(snippet_entry))
                dir_entry.addChild(snippet_entry)
                self.sm.available_snippets[item.snippet_uuid].directory = dir_uuid
