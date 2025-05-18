from .extended_abstract_desk_item import ExtendedAbstractDeskItem
from PySide6.QtWidgets import QGraphicsItem, QDialog, QVBoxLayout
from PySide6.QtGui import QPen, QKeySequence, QPainter, QStaticText
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QKeyCombination, QTimer, Signal

class DeskButtonConfig(QDialog):
    configuration_completed = Signal(dict)

    def __init__(self, window, label: str, linked_controller_uuid: str, hotkey: str, mode: str, mode_duration: int) -> None:
        """
        Create a dialog for configuring a button
        :param window: The main window
        :param label: The label of the button
        :param linked_controller_uuid: The UUID of the linked controller
        :param hotkey: The hotkey of the button
        :param mode: The mode of the button (toggle, flash)
        :param mode_duration: The duration of the flash mode
        """
        super().__init__()
        self.window = window
        self.label = label
        self.linked_controller_uuid = linked_controller_uuid
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
        self.ui.link_controller_btn.clicked.connect(self.link_controller)
        self.ui.unlink_controller_btn.clicked.connect(self.unlink_controller)
        self.ui.clear_hotkey_btn.clicked.connect(lambda: self.ui.hotkey_edit.clear())
        self.ui.select_hotkey_btn.clicked.connect(self.start_key_capture)#
        self.ui.toggle_mode_radio.toggled.connect(lambda: self.set_mode("toggle"))
        self.ui.flash_mode_radio.toggled.connect(lambda: self.set_mode("flash"))

        # Set the initial values
        self.ui.label_edit.setText(self.label)
        self.ui.controller_edit.setText(linked_controller_uuid)
        self.ui.hotkey_edit.setText(hotkey)
        if mode == "toggle":
            self.ui.toggle_mode_radio.setChecked(True)
        else:
            self.ui.flash_mode_radio.setChecked(True)
        self.ui.flash_duration_spin.setValue(mode_duration)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def link_controller(self) -> None:
        """
        Links the controller to the button
        :return: None
        """
        self.setVisible(False)
        self.window.control_desk_view.linking_completed.connect(self.on_linking_completed)
        self.window.control_desk_view.link_desk_item("controller")

    def unlink_controller(self) -> None:
        """
        Unlinks the controller from the button
        :return: None
        """
        self.linked_controller_uuid = None
        self.ui.controller_edit.clear()

    def on_linking_completed(self, result: str) -> None:
        """
        Handles the result of the linking operation
        :param result: The UUID of the linked controller
        """
        self.window.control_desk_view.linking_completed.disconnect(self.on_linking_completed)
        self.linked_controller_uuid = result
        self.ui.controller_edit.setText(result)
        self.setVisible(True)

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

    def accept(self) -> None:
        """
        Override accept to emit configuration_completed signal before closing
        :return: None
        """
        config = {
            'label': self.ui.label_edit.text(),
            'linked_controller_uuid': self.linked_controller_uuid,
            'hotkey': self.ui.hotkey_edit.text(),
            'mode': self.mode,
            'mode_duration': self.ui.flash_duration_spin.value()
        }
        self.configuration_completed.emit(config)
        super().accept()

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

class DeskButton(ExtendedAbstractDeskItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int,
                label: str = "Button", linked_controller_uuid: str = None, uuid: str = None,
                hotkey: str = None, mode: str = "toggle", mode_duration: int = 0) -> None:
        """
        Create a button object
        :param desk: The control desk object
        :param x: The x position of the button
        :param y: The y position of the button
        :param width: The width of the button
        :param height: The height of the button
        :param label: The label of the button
        :param linked_controller_uuid: The UUID of the snippet to link to
        :param uuid: The UUID of the button
        :param hotkey: The hotkey of the button
        :param mode: The mode of the button (toggle, flash)
        :param mode_duration: The duration of the flash mode
        """
        super().__init__(desk, x, y, width, height, uuid)
        self.label = label
        self.linked_controller_uuid = linked_controller_uuid
        self.desk = desk
        self.pressed = False
        self.hotkey = hotkey
        self.mode = mode
        self.mode_duration = mode_duration
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.deactivation_timer = QTimer()
        self.deactivation_timer.setSingleShot(True)
        self.deactivation_timer.timeout.connect(lambda: self.clicked())

        self.setPos(x, y)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        brush_color = Qt.lightGray
        if self.pressed:
            brush_color = Qt.darkGray
            painter.setPen(QPen(Qt.green, 2))
        super().paint(painter, option, widget, brush_color)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawStaticText(0, 0, QStaticText(self.label))

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
        self.update()
        controller = self.desk.get_item_with_uuid(self.linked_controller_uuid)
        if self.pressed:
            if self.mode == "flash":  # Disable the button after the mode duration, if in flash mode
                self.deactivation_timer.start(self.mode_duration)
            if controller:
                controller.activate()
        else:
            if self.deactivation_timer.isActive():  # Stop the timer if it is active
                self.deactivation_timer.stop()
            controller.deactivate()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the button's properties
        """
        if self.desk.window.live_mode or self.desk.is_linking:
            return  # Disable editing in live mode or when linking
        config_dlg = DeskButtonConfig(window=self.desk.window, label=self.label,
                                      linked_controller_uuid=self.linked_controller_uuid, hotkey=self.hotkey,
                                      mode = self.mode, mode_duration = self.mode_duration)
        config_dlg.configuration_completed.connect(self.apply_configuration)
        config_dlg.exec()
        super().mouseDoubleClickEvent(event)

    def apply_configuration(self, config: dict) -> None:
        """
        Apply configuration changes from the dialog
        :param config: The configuration dictionary
        :return: None
        """
        self.label = config['label']
        self.linked_controller_uuid = config['linked_controller_uuid']
        self.hotkey = config['hotkey']
        self.desk.regenerate_hotkeys()
        self.mode = config['mode']
        self.mode_duration = config['mode_duration']
        self.update()
