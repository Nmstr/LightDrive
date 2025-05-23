from Workspace.Widgets.ShowEditor.show_editor import ShowEditor
from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QVBoxLayout, QDialog, \
    QDialogButtonBox, QAbstractItemView, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
import uuid

class AddSoundResourceDialog(QDialog):
    def __init__(self, window) -> None:
        """
        Create a dialog for selecting a sound resource
        :param window: The main window
        """
        super().__init__()
        self.setWindowTitle("LightDrive - Select Sound Resource For Show")
        self.window = window

        layout = QVBoxLayout()
        self.sound_resource_list = QListWidget()
        self.load_sound_resources()
        layout.addWidget(self.sound_resource_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def load_sound_resources(self) -> None:
        """
        Loads the sound resources and shows them in sound_resource_list
        :return: None
        """
        for snippet in self.window.snippet_manager.available_snippets.values():
            if snippet.type == "sound_resource":
                item = QListWidgetItem(self.sound_resource_list)
                item.setText(snippet.name)
                item.snippet_uuid = snippet.uuid
                self.sound_resource_list.addItem(item)

class ShowAddSnippetsDialog(QDialog):
    def __init__(self, window) -> None:
        """
        Create a dialog for adding snippets to a show
        :param window: The main window
        """
        super().__init__()
        self.setWindowTitle("LightDrive - Add Snippet To Show")
        self.window = window

        layout = QVBoxLayout()
        self.snippet_tree = QTreeWidget()
        self.snippet_tree.setHeaderHidden(True)
        self.snippet_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
                if self.window.snippet_manager.available_snippets[child.uuid].type == "show":
                    continue
                if self.window.snippet_manager.available_snippets[child.uuid].type == "sound_resource":
                    continue
                if self.window.snippet_manager.available_snippets[child.uuid].type == "script":
                    continue
                new_item = QTreeWidgetItem(target_parent)
                new_item.setText(0, child.text(0))
                new_item.snippet_uuid = child.uuid
                add_items(child, new_item)

        root = self.window.ui.snippet_selector_tree.invisibleRootItem()
        add_items(root, self.snippet_tree)

@dataclass
class ShowData:
    uuid: str
    name: str
    type: str = field(default="show", init=False)
    directory: str = field(default="root")
    sound_resource_uuid: str = field(default=None)
    added_snippets: dict = field(default_factory=dict)

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

    def show_play(self) -> None:
        """
        Plays the current show
        :return: None
        """
        self.show_editor.play()

    def show_pause(self) -> None:
        """
        Pauses the current show
        :return: None
        """
        self.show_editor.pause()

    def show_stop(self) -> None:
        """
        Stops the current show
        :return: None
        """
        self.show_editor.stop()

    def show_toggle_show(self) -> None:
        """
        Toggles showing the show
        :return: None
        """
        self.show_editor.toggle_show(self.sm.window.ui.show_show_btn.isChecked())

    def show_set_volume(self, volume: int) -> None:
        """
        Sets the volume of the current show
        :param volume: The volume to set
        :return: None
        """
        self.show_editor.set_volume(volume)

    def show_add_snippets(self, snippet_uuids: list = None) -> None:
        """
        Adds a snippet to the current show
        :param snippet_uuids: The uuids of the snippets to add (default: dialog selection)
        :return: None
        """
        if not snippet_uuids:  # If no snippets are provided, show the dialog
            dlg = ShowAddSnippetsDialog(self.sm.window)
            if dlg.exec():
                snippets = dlg.snippet_tree.selectedItems()
                snippet_uuids = [snippet.snippet_uuid for snippet in snippets]

        for snippet_uuid in snippet_uuids:  # Check each snippet
            snippet = self.sm.available_snippets.get(snippet_uuid)
            if snippet.type == "show":
                snippet_uuids.remove(snippet.uuid)
            elif snippet.type == "sound_resource":
                snippet_uuids.remove(snippet.uuid)
            elif snippet.type == "script":
                snippet_uuids.remove(snippet.uuid)
            elif snippet.type == "directory":
                err_msg = QMessageBox(QMessageBox.Critical, "LightDrive - Error", "Cant add directory to show", QMessageBox.Ok)
                err_msg.exec()
                snippet_uuids.remove(snippet.uuid)

        for snippet_uuid in snippet_uuids:
            self.show_editor.add_snippet(snippet_uuid)

    def show_load_song(self, show_uuid: str = None, sound_resource_uuid: str = None) -> None:
        """
        Adds a sound resource to the show
        :param show_uuid: The uuid of the show to add the sound resource to (default: current show)
        :param sound_resource_uuid: The uuid of the sound resource to add (default: dialog selection)
        :return:
        """
        if not show_uuid:
            show_uuid = self.sm.current_snippet.uuid
        if not sound_resource_uuid:
            dlg = AddSoundResourceDialog(self.sm.window)
            if dlg.exec():
                sound_resource_uuid = dlg.sound_resource_list.selectedItems()[0].snippet_uuid
        show_snippet = self.sm.available_snippets.get(show_uuid)
        show_snippet.sound_resource_uuid = sound_resource_uuid
        self.show_editor.load_player()
        self.show_editor.load_audio_background()
