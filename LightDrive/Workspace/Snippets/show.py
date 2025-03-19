from Workspace.Widgets.show_editor import ShowEditor
from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

@dataclass
class ShowData:
    uuid: str
    name: str
    type: str = field(default="show", init=False)
    directory: str = field(default="root")

class ShowManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def show_display(self, show_uuid: str) -> None:
        """
        Displays the show editor for the given show uuid
        :param show_uuid: The uuid of the show to display
        :return: None
        """
        self._load_show_editor(show_uuid)

    def _load_show_editor(self, show_uuid: str) -> None:
        """
        Loads the show editor of the current show to ui.show_editor_frame
        :return: None
        """
        layout = clear_field(self.sm.window.ui.show_editor_frame, QVBoxLayout, amount_left = 0)
        show_snippet = self.sm.available_snippets.get(show_uuid)
        self.show_editor = ShowEditor(self.sm.window, show_snippet)
        layout.addWidget(self.show_editor)

    def show_create(self, *, parent: QTreeWidgetItem = None, show_data: ShowData = None) -> None:
        """
        Creates a show in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param show_data: The data of the show (only if importing)
        :return: None
        """
        show_entry = QTreeWidgetItem()
        show_entry.setIcon(0, QPixmap("Assets/Icons/show.svg"))
        if not show_data:
            show_uuid = str(uuid.uuid4())
            show_data = ShowData(show_uuid, "New Show")
        show_entry.uuid = show_data.uuid
        self.sm.available_snippets[show_data.uuid] = show_data

        show_entry.setText(0, self.sm.available_snippets[show_data.uuid].name)
        self.sm.add_item(show_entry, parent)

    def show_rename(self, show_uuid: str = None, new_name: str = None) -> None:
        """
        Renames the show with the given uuid
        :param show_uuid: The uuid of the show to rename
        :param new_name: The new name of the show
        :return: None
        """
        if not show_uuid:
            show_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.show_name_edit.text()
        show_snippet = self.sm.available_snippets.get(show_uuid)
        show_snippet.name = new_name
        show_entry = self.sm.find_snippet_entry_by_uuid(show_uuid)
        show_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
