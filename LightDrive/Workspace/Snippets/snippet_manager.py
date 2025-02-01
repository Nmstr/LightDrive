from Workspace.Snippets.scene import SceneManager
from Workspace.Snippets.cue import CueManager
from Workspace.Snippets.rgb_matrix import RgbMatrixManager
from Workspace.Snippets.script import ScriptManager
from Workspace.Snippets.two_d_efx import TwoDEfxManager
from Workspace.Snippets.directory import DirectoryManager
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt

class SnippetManager:
    def __init__(self, window = None):
        """
        Creates the snippet manager
        :param window: The application's main window
        """
        self.available_snippets = {}
        self.current_snippet = None
        self.current_display_snippet = None
        self.window = window

        self.scene_manager = SceneManager(self)
        self.cue_manager = CueManager(self)
        self.rgb_matrix_manager = RgbMatrixManager(self)
        self.script_manager = ScriptManager(self)
        self.two_d_efx_manager = TwoDEfxManager(self)
        self.directory_manager = DirectoryManager(self)

    def add_item(self, item: QTreeWidgetItem, parent: QTreeWidgetItem = None) -> None:
        """
        Adds the provided item to the snippet selector tree
        :param item: The item to add
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        selector_tree = self.window.ui.snippet_selector_tree
        if parent:  # Used for importing snippets
            parent.addChild(item)
            parent.setExpanded(True)
            return
        if selector_tree.selectedItems() and selector_tree.selectedItems()[0].extra_data["type"] == "directory":
            selector_tree.selectedItems()[0].addChild(item)
            selector_tree.selectedItems()[0].setExpanded(True)
        else:
            selector_tree.addTopLevelItem(item)
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def show_editor(self, item) -> None:
        """
        Shows the snippet editor for the selected snippet
        :param item: The snippet to edit
        :return: None
        """
        self.current_snippet = self.available_snippets[item.uuid]
        match self.current_snippet.type:
            case "directory":
                self.window.ui.snippet_editor.setCurrentIndex(1)
                self.window.ui.directory_name_edit.setText(self.current_snippet.name)
            case "cue":
                self.window.ui.snippet_editor.setCurrentIndex(2)
                self.window.ui.cue_name_edit.setText(self.current_snippet.name)
                self._load_cue_timeline()
            case "scene":
                self.window.ui.snippet_editor.setCurrentIndex(6)
                self.window.ui.scene_name_edit.setText(self.current_snippet.name)
                self._scene_load_fixtures(self.current_snippet.get("fixtures", []))
            case "two_d_efx":
                self.window.ui.snippet_editor.setCurrentIndex(3)
            case "rgb_matrix":
                self.window.ui.snippet_editor.setCurrentIndex(4)
            case "script":
                self.window.ui.snippet_editor.setCurrentIndex(5)

    def find_snippet_by_uuid(self, snippet_uuid: str) -> dict:
        """
        Finds a snippet by its UUID
        :param snippet_uuid: The UUID of the snippet to find
        :return: The data of the snippet
        """
        def _find_snippet_by_uuid(snippet_config, target_uuid: str) -> dict:
            if isinstance(snippet_config, list):
                for snippet in snippet_config:
                    if snippet["uuid"] == target_uuid:
                        return snippet
                    if snippet["type"] == "directory" and "content" in snippet:
                        result = _find_snippet_by_uuid(snippet["content"], target_uuid)
                        if result:
                            return result
            elif isinstance(snippet_config, dict):
                for key, snippet in snippet_config.items():
                    if snippet["uuid"] == target_uuid:
                        return snippet
                    if snippet["type"] == "directory" and "content" in snippet:
                        result = _find_snippet_by_uuid(snippet["content"], target_uuid)
                        if result:
                            return result
            return {}

        snippet_configuration = self.window.workspace_file_manager.get_snippet_configuration()
        return _find_snippet_by_uuid(snippet_configuration, snippet_uuid)

    def find_snippet_entry_by_uuid(self, snippet_uuid: str) -> QTreeWidgetItem | None:
        """
        Finds a snippet entry by its UUID
        :param snippet_uuid: The UUID of the snippet to find
        :return: The QTreeWidgetItem of the snippet
        """
        def _find_snippet_entry_by_uuid(snippet_entry, target_uuid: str) -> QTreeWidgetItem | None:
            if snippet_entry.uuid == target_uuid:
                return snippet_entry
            for i in range(snippet_entry.childCount()):
                result = _find_snippet_entry_by_uuid(snippet_entry.child(i), target_uuid)
                if result:
                    return result
            return None

        snippet_selector_tree = self.window.ui.snippet_selector_tree
        for i in range(snippet_selector_tree.topLevelItemCount()):
            result = _find_snippet_entry_by_uuid(snippet_selector_tree.topLevelItem(i), snippet_uuid)
            if result:
                return result
        return None
