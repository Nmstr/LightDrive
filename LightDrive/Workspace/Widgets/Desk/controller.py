from .extended_abstract_desk_item import ExtendedAbstractDeskItem
from Backend.output import OutputSnippet
from Backend.snippets import SequenceOutputSnippet, TwoDEfxOutputSnippet
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QDialogButtonBox
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt

class SnippetLinkingSelection(QDialog):
    def __init__(self, window) -> None:
        """
        Create a dialog for selecting a snippet to link to
        :param window: The main window
        """
        super().__init__()
        self.setWindowTitle("LightDrive - Snippet Linking")
        self.window = window

        layout = QVBoxLayout()
        self.snippet_tree = QTreeWidget()
        self.snippet_tree.setHeaderHidden(True)
        self.snippet_tree.itemDoubleClicked.connect(self.accept)
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

class DeskControllerConfig(QDialog):
    def __init__(self, window, linked_snippet_uuid: str) -> None:
        """
        Create a dialog for configuring a controller
        :param window: The main window
        :param linked_snippet_uuid: The UUID of the linked snippet
        """
        super().__init__()
        self.window = window
        self.linked_snippet_uuid = linked_snippet_uuid

        self.setWindowTitle("LightDrive - Controller Properties")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/desk_controller_config.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)
        self.ui.link_snippet_btn.clicked.connect(self.link_snippet)
        self.ui.unlink_snippet_btn.clicked.connect(self.unlink_snippet)

        # Set the initial values
        snippet_data = self.window.snippet_manager.available_snippets.get(linked_snippet_uuid)
        if snippet_data:
            self.ui.snippet_edit.setText(snippet_data.name)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def link_snippet(self) -> None:
        """
        Open the snippet linking dialog
        """
        link_dlg = SnippetLinkingSelection(self.window)
        if link_dlg.exec():
            selected_uuid = link_dlg.snippet_tree.currentItem().snippet_uuid
            snippet_data = self.window.snippet_manager.available_snippets.get(selected_uuid)
            self.ui.snippet_edit.setText(snippet_data.name)
            self.linked_snippet_uuid = selected_uuid

    def unlink_snippet(self) -> None:
        """
        Unlink the snippet
        """
        self.linked_snippet_uuid = None
        self.ui.snippet_edit.clear()

class DeskController(ExtendedAbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int, uuid: str, linked_snippet_uuid: str = None) -> None:
        """
        Create a desk controller
        :param desk: The control desk
        :param x: The x position of the controller
        :param y: The y position of the controller
        :param width: The width of the controller
        :param height: The height of the controller
        :param uuid: The UUID of the controller
        :param linked_snippet_uuid: The UUID of the linked snippet
        """
        super().__init__(desk, x, y, width, height, uuid)
        self.desk = desk
        self.linked_snippet_uuid = linked_snippet_uuid
        self.output_snippet = None

    def activate(self) -> None:
        """
        Activate the controller
        :return: None
        """
        linked_snippet = self.desk.window.snippet_manager.available_snippets.get(self.linked_snippet_uuid)
        if not linked_snippet:
            return
        if linked_snippet.type == "scene":
            values = self.desk.window.snippet_manager.scene_manager.scene_construct_output_values(self.linked_snippet_uuid)
            if values:
                self.output_snippet = OutputSnippet(self.desk.window.dmx_output, values)
                self.desk.window.dmx_output.insert_snippet(self.output_snippet)
        elif linked_snippet.type == "sequence":
            self.output_snippet = SequenceOutputSnippet(self.desk.window, self.linked_snippet_uuid)
            self.desk.window.dmx_output.insert_snippet(self.output_snippet)
        elif linked_snippet.type == "two_d_efx":
            self.output_snippet = TwoDEfxOutputSnippet(self.desk.window, self.linked_snippet_uuid)
            self.desk.window.dmx_output.insert_snippet(self.output_snippet)

    def deactivate(self) -> None:
        """
        Deactivate the controller
        :return: None
        """
        if self.output_snippet:  # Remove the output snippet if it exists (stops output)
            self.desk.window.dmx_output.remove_snippet(self.output_snippet)
            self.output_snippet = None

    def paint(self, painter: QPainter, option, widget=None) -> None:
        super().paint(painter, option, widget, brush_color=Qt.transparent)
        pixmap = QPixmap("Assets/Icons/desk_controller.svg")
        painter.drawPixmap(0, 0, pixmap.scaled(self.width, self.height, Qt.KeepAspectRatio))

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the label's properties
        """
        if self.desk.window.live_mode or self.desk.is_linking:
            return  # Disable editing in live mode or when linking
        config_dlg = DeskControllerConfig(window=self.desk.window, linked_snippet_uuid=self.linked_snippet_uuid)
        if config_dlg.exec():
            self.linked_snippet_uuid = config_dlg.linked_snippet_uuid
        super().mouseDoubleClickEvent(event)
