from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import uuid

class SnippetManager:
    def __init__(self, window = None):
        """
        Creates the snippet manager
        :param window: The application's main window
        """
        self.current_snippet = None
        self.window = window

    def snippet_create_cue(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a cue in the snippet selector tree
        :param extra_data: Any extra data for the cue (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_cue = QTreeWidgetItem()
        new_cue.setIcon(0, QPixmap("Assets/Icons/cue.svg"))
        if extra_data:
            new_cue.extra_data = extra_data
        else:
            new_cue.extra_data = {
                "type": "cue",
                "uuid": str(uuid.uuid4()),
                "name": "New Cue",
            }
        new_cue.setText(0, new_cue.extra_data["name"])
        self.snippet_add_item(new_cue, parent)

    def snippet_create_scene(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a scene in the snippet selector tree
        :param extra_data: Any extra data for the scene (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_scene = QTreeWidgetItem()
        new_scene.setIcon(0, QPixmap("Assets/Icons/scene.svg"))
        if extra_data:
            new_scene.extra_data = extra_data
        else:
            new_scene.extra_data = {
                "type": "scene",
                "uuid": str(uuid.uuid4()),
                "name": "New Scene",
            }
        new_scene.setText(0, new_scene.extra_data["name"])
        self.snippet_add_item(new_scene, parent)

    def snippet_create_efx_2d(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a 2d efx in the snippet selector tree
        :param extra_data: Any extra data for the 2d efx (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_efx_2d = QTreeWidgetItem()
        new_efx_2d.setIcon(0, QPixmap("Assets/Icons/efx_2d.svg"))
        if extra_data:
            new_efx_2d.extra_data = extra_data
        else:
            new_efx_2d.extra_data = {
                "type": "efx_2d",
                "uuid": str(uuid.uuid4()),
                "name": "New 2D EFX",
            }
        new_efx_2d.setText(0, new_efx_2d.extra_data["name"])
        self.snippet_add_item(new_efx_2d, parent)

    def snippet_create_rgb_matrix(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a rgb matrix in the snippet selector tree
        :param extra_data: Any extra data for the rgb matrix (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_rgb_matrix = QTreeWidgetItem()
        new_rgb_matrix.setIcon(0, QPixmap("Assets/Icons/rgb_matrix.svg"))
        if extra_data:
            new_rgb_matrix.extra_data = extra_data
        else:
            new_rgb_matrix.extra_data = {
                "type": "rgb_matrix",
                "uuid": str(uuid.uuid4()),
                "name": "New RGB Matrix",
            }
        new_rgb_matrix.setText(0, new_rgb_matrix.extra_data["name"])
        self.snippet_add_item(new_rgb_matrix, parent)

    def snippet_create_script(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> None:
        """
        Creates a script in the snippet selector tree
        :param extra_data: Any extra data for the script (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: None
        """
        new_script = QTreeWidgetItem()
        new_script.setIcon(0, QPixmap("Assets/Icons/script.svg"))
        if extra_data:
            new_script.extra_data = extra_data
        else:
            new_script.extra_data = {
                "type": "script",
                "uuid": str(uuid.uuid4()),
                "name": "New Script",
            }
        new_script.setText(0, new_script.extra_data["name"])
        self.snippet_add_item(new_script, parent)

    def snippet_create_dir(self, *, extra_data: dict = None, parent: QTreeWidgetItem = None) -> QTreeWidgetItem:
        """
        Creates a directory in the snippet selector tree
        :param extra_data: Any extra data for the directory (only if importing)
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :return: The created directory item
        """
        new_dir = QTreeWidgetItem()
        new_dir.setIcon(0, QPixmap("Assets/Icons/directory.svg"))
        if extra_data:
            new_dir.extra_data = extra_data
        else:
            new_dir.extra_data = {
                "type": "directory",
                "uuid": str(uuid.uuid4()),
                "name": "New Directory",
            }
        new_dir.setText(0, new_dir.extra_data["name"])
        self.snippet_add_item(new_dir, parent)
        return new_dir

    def snippet_add_item(self, item: QTreeWidgetItem, parent: QTreeWidgetItem = None) -> None:
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

    def snippet_show_editor(self, item) -> None:
        """
        Shows the snippet editor for the selected snippet
        :param item: The snippet to edit
        :return: None
        """
        match item.extra_data["type"]:
            case "directory":
                self.window.ui.snippet_editor.setCurrentIndex(1)
                self.window.ui.directory_name_edit.setText(item.extra_data["name"])
            case "cue":
                self.window.ui.snippet_editor.setCurrentIndex(2)
            case "scene":
                self.window.ui.snippet_editor.setCurrentIndex(6)
            case "efx_2d":
                self.window.ui.snippet_editor.setCurrentIndex(3)
            case "rgb_matrix":
                self.window.ui.snippet_editor.setCurrentIndex(4)
            case "script":
                self.window.ui.snippet_editor.setCurrentIndex(5)
        self.current_snippet = item

    def snippet_rename_dir(self) -> None:
        """
        Renames the directory to the new name
        :return: None
        """
        self.current_snippet.extra_data["name"] = self.window.ui.directory_name_edit.text()
        self.current_snippet.setText(0, self.window.ui.directory_name_edit.text())
        self.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)
