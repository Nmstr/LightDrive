from .abstract_desk_item import AbstractDeskItem
from Backend.output import OutputSnippet
from PySide6.QtWidgets import QGraphicsItem, QDialog, QVBoxLayout, QGraphicsTextItem, QTreeWidget, QTreeWidgetItem, QDialogButtonBox
from PySide6.QtGui import QPen, QKeySequence
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QKeyCombination, QTimer

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
    def __init__(self, window, button_label: str, linked_snippet_uuid: str, hotkey: str, mode: str, mode_duration: int) -> None:
        """
        Create a dialog for configuring a button
        :param window: The main window
        :param button_label: The label of the button
        :param linked_snippet_uuid: The UUID of the linked snippet
        :param hotkey: The hotkey of the button
        :param mode: The mode of the button (toggle, flash)
        :param mode_duration: The duration of the flash mode
        """
        super().__init__()
        self.window = window
        self.button_label = button_label
        self.linked_snippet_uuid = linked_snippet_uuid
        self.mode = mode
        self.mode_duration = mode_duration
        self.capturing = False

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
        self.ui.clear_hotkey_btn.clicked.connect(lambda: self.ui.hotkey_edit.clear())
        self.ui.select_hotkey_btn.clicked.connect(self.start_key_capture)#
        self.ui.toggle_mode_radio.toggled.connect(lambda: self.set_mode("toggle"))
        self.ui.flash_mode_radio.toggled.connect(lambda: self.set_mode("flash"))

        # Set the initial values
        self.ui.label_edit.setText(self.button_label)
        snippet_data = self.window.snippet_manager.find_snippet_by_uuid(linked_snippet_uuid)
        if snippet_data:
            self.ui.snippet_edit.setText(snippet_data["name"])
        self.ui.hotkey_edit.setText(hotkey)
        if mode == "toggle":
            self.ui.toggle_mode_radio.setChecked(True)
        else:
            self.ui.flash_mode_radio.setChecked(True)
        self.ui.flash_duration_spin.setValue(mode_duration)

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

    def start_key_capture(self) -> None:
        """
        Starts capturing a key combination for the hotkey
        :return: None
        """
        self.capturing = True
        self.ui.hotkey_edit.setText("")
        self.ui.hotkey_edit.setFocus()

    def keyPressEvent(self, event):  # noqa: N802
        """
        Handle key presses for capturing hotkeys
        :param event: The key press event
        :return: None
        """
        if self.capturing:  # Only capture keys if capturing is enabled
            if event.key() == Qt.Key_Escape:
                self.capturing = False
                return  # Stop capturing on escape
            if (event.key() == Qt.Key_Shift
                    or event.key() == Qt.Key_Control
                    or event.key() == Qt.Key_Alt):
                return  # Ignore modifier keys so that they can be used in combination
            key_combination = QKeyCombination(event.modifiers(), Qt.Key(event.key()))
            key_sequence = QKeySequence(key_combination)
            self.ui.hotkey_edit.setText(key_sequence.toString())
            self.capturing = False
        super().keyPressEvent(event)

    def set_mode(self, mode: str) -> None:
        """
        Set the mode of the button
        :param mode: The mode of the button
        :return: None
        """
        self.mode = mode
        if mode == "toggle":
            self.ui.flash_duration_spin.setEnabled(False)
        elif mode == "flash":
            self.ui.flash_duration_spin.setEnabled(True)

class DeskButton(AbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int,
                button_label: str = "Button", linked_snippet_uuid: str = None, button_uuid: str = None,
                hotkey: str = None, mode: str = "toggle", mode_duration: int = 0) -> None:
        """
        Create a button object
        :param desk: The control desk object
        :param x: The x position of the button
        :param y: The y position of the button
        :param width: The width of the button
        :param height: The height of the button
        :param button_label: The label of the button
        :param linked_snippet_uuid: The UUID of the snippet to link to
        :param button_uuid: The UUID of the button
        :param hotkey: The hotkey of the button
        :param mode: The mode of the button (toggle, flash)
        :param mode_duration: The duration of the flash mode
        """
        super().__init__(desk, x, y, width, height)
        self.button_label = button_label
        self.linked_snippet_uuid = linked_snippet_uuid
        self.desk = desk
        self.pressed = False
        self.output_snippet = None
        self.button_uuid = button_uuid
        self.hotkey = hotkey
        self.mode = mode
        self.mode_duration = mode_duration
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.deactivation_timer = QTimer()
        self.deactivation_timer.setSingleShot(True)
        self.deactivation_timer.timeout.connect(lambda: self.clicked())

        self.label = QGraphicsTextItem(self.button_label)
        self.label.setPos(x, y)
        self.label.setDefaultTextColor(Qt.black)
        self.addToGroup(self.label)

        self.setPos(x, y)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Activate or deactivate the button using the self.clicked method
        """
        self.clicked()
        super().mousePressEvent(event)

    def clicked(self) -> None:
        """
        Handle the button click. This is here so that the button can be clicked programmatically (hotkeys). mousePressEvent just calls this.
        :return:
        """
        if not self.desk.window.live_mode:
            return  # Disallow button press outside live mode

        self.pressed = not self.pressed
        if self.pressed:
            self.body.setBrush(Qt.darkGray)
            self.body.setPen(QPen(Qt.green, 2))
            values = self.desk.window.snippet_manager.scene_construct_output_values(self.linked_snippet_uuid)
            if values:
                self.output_snippet = OutputSnippet(self.desk.window.dmx_output, values)
                self.desk.window.dmx_output.insert_snippet(self.output_snippet)

            if self.mode == "flash":  # Disable the button after the mode duration, if in flash mode
                self.deactivation_timer.start(self.mode_duration)
        else:
            self.body.setBrush(Qt.lightGray)
            self.body.setPen(QPen(Qt.black, 1))
            if self.deactivation_timer.isActive():  # Stop the timer if it is active
                self.deactivation_timer.stop()
            if self.output_snippet:  # Remove the output snippet if it exists (stops output)
                self.desk.window.dmx_output.remove_snippet(self.output_snippet)
                self.output_snippet = None

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the button's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskButtonConfig(window=self.desk.window, button_label=self.button_label,
                                      linked_snippet_uuid=self.linked_snippet_uuid, hotkey=self.hotkey,
                                      mode = self.mode, mode_duration = self.mode_duration)
        if config_dlg.exec():
            self.button_label = config_dlg.ui.label_edit.text()
            self.label.setPlainText(config_dlg.ui.label_edit.text())
            self.linked_snippet_uuid = config_dlg.linked_snippet_uuid
            self.hotkey = config_dlg.ui.hotkey_edit.text()
            self.desk.regenerate_hotkeys()
            self.mode = config_dlg.mode
            self.mode_duration = config_dlg.ui.flash_duration_spin.value()
        super().mouseDoubleClickEvent(event)
