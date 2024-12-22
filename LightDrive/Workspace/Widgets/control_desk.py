from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QDialog, \
    QVBoxLayout, QGraphicsItemGroup, QGraphicsTextItem, QTreeWidget, QTreeWidgetItem, QDialogButtonBox
from PySide6.QtGui import QPen
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
                new_item.snippet_uuid = child.extra_data["uuid"]
                add_items(child, new_item)

        root = self.window.ui.snippet_selector_tree.invisibleRootItem()
        add_items(root, self.snippet_tree)

class DeskButtonConfig(QDialog):
    def __init__(self, window, button_data) -> None:
        """
        Create a dialog for configuring a button
        :param window: The main window
        :param button_data: The data for the button (created if not provided)
        """
        super().__init__()
        self.window = window
        self.setWindowTitle("LightDrive - Button Properties")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/desk_button_config.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)
        self.ui.link_snippet_btn.clicked.connect(self.link_snippet)

        self.ui.label_edit.setText(button_data["label"])
        snippet_data = self.window.snippet_manager.find_snippet_by_uuid(button_data["snippet_uuid"])
        if snippet_data:
            self.ui.snippet_edit.setText(snippet_data["name"])
        self.linked_snippet_uuid = button_data["snippet_uuid"]

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
            snippet_data = self.window.snippet_manager.find_snippet_by_uuid(selected_uuid)
            self.ui.snippet_edit.setText(snippet_data["name"])
            self.linked_snippet_uuid = selected_uuid

class DeskButton(QGraphicsItemGroup):
    def __init__(self, desk, x, y, width, height, button_data = None) -> None:
        """
        Create a button object
        :param button_data: The data for the button (created if not provided)
        """
        super().__init__()
        if not button_data:
            self.button_data = {
                "label": "Button",
                "snippet_uuid": None
            }
        self.desk = desk
        self.pressed = False
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.body = QGraphicsRectItem(x, y, width, height)
        self.body.setBrush(Qt.lightGray)
        self.addToGroup(self.body)
        self.label = QGraphicsTextItem(self.button_data["label"])
        self.label.setDefaultTextColor(Qt.black)
        self.addToGroup(self.label)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Activate or deactivate the button
        """
        if not self.desk.window.live_mode:
            return  # Disallow button press outside live mode

        self.pressed = not self.pressed
        if self.pressed:
            self.body.setBrush(Qt.darkGray)
            self.body.setPen(QPen(Qt.green, 2))
        else:
            self.body.setBrush(Qt.lightGray)
            self.body.setPen(QPen(Qt.black, 1))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the button's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskButtonConfig(window=self.desk.window, button_data=self.button_data)
        if config_dlg.exec():
            self.button_data["label"] = config_dlg.ui.label_edit.text()
            self.label.setPlainText(config_dlg.ui.label_edit.text())
            self.button_data["snippet_uuid"] = config_dlg.linked_snippet_uuid
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        """
        Move the button
        """
        if self.desk.window.live_mode:
            return  # Disable movement in live mode
        super().mouseMoveEvent(event)

class ControlDesk(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the control desk object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)

    def add_btn(self) -> None:
        """
        Add a button to the control desk
        """
        button = DeskButton(self, 0, 0, 100, 100)
        self.scene.addItem(button)

    def add_fader(self) -> None:
        """
        Add a slider to the control desk
        """
        pass

    def add_knob(self) -> None:
        """
        Add a knob to the control desk
        """
        pass

    def add_sound_trigger(self) -> None:
        """
        Add a sound trigger to the control desk
        """
        pass

    def add_label(self) -> None:
        """
        Add a label to the control desk
        """
        pass

    def add_clock(self) -> None:
        """
        Add a clock to the control desk
        """
        pass
