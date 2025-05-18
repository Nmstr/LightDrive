from Workspace.Widgets.Desk import DeskButton, DeskLabel, DeskClock, DeskController, DeskWire
from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Signal
import uuid

class ControlDesk(QGraphicsView):
    linking_completed = Signal(object)

    def __init__(self, window: QMainWindow) -> None:
        """
        Create the control desk object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1920, 1080)
        self.scene_items = []
        self.available_hotkeys = []
        self.is_linking = None

    def add_controller(self) -> None:
        """
        Add a controller to the control desk
        """
        controller = DeskController(self, 0, 0, 50, 50, uuid=str(uuid.uuid4()))
        self.scene.addItem(controller)
        self.scene_items.append(controller)

    def add_btn(self) -> None:
        """
        Add a button to the control desk
        """
        button = DeskButton(self, 0, 0, 100, 100, uuid=str(uuid.uuid4()))
        self.scene.addItem(button)
        self.scene_items.append(button)
        self.regenerate_hotkeys()

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
        label = DeskLabel(self, 0, 0, 150, 40, uuid=str(uuid.uuid4()), text="Label")
        self.scene.addItem(label)
        self.scene_items.append(label)

    def add_clock(self) -> None:
        """
        Add a clock to the control desk
        """
        clock = DeskClock(self, 0, 0, 150, 40, uuid=str(uuid.uuid4()), polling_rate=1000)
        self.scene.addItem(clock)
        self.scene_items.append(clock)

    def load_desk_configuration(self, configuration: list) -> None:
        """
        Load the configuration of the control desk. Used for loading a saved configuration when opening a workspace.
        :param configuration: The configuration of the control desk to load
        :return: None
        """
        for item in configuration:
            if item["type"] == "button":
                button = DeskButton(self, item["x"], item["y"], item["width"], item["height"],
                                    label=item.get("label", None), linked_controller_uuid=item.get("linked_controller_uuid", None),
                                    uuid=item.get("uuid", None), hotkey=item.get("hotkey", None), mode=item.get("mode", "toggle"),
                                    mode_duration=item.get("mode_duration", 0))
                self.scene.addItem(button)
                self.scene_items.append(button)
            elif item["type"] == "label":
                label = DeskLabel(self, item["x"], item["y"], item["width"], item["height"],
                            uuid=item.get("uuid", None), text=item.get("label", "Label"))
                self.scene.addItem(label)
                self.scene_items.append(label)
            elif item["type"] == "clock":
                clock = DeskClock(self, item["x"], item["y"], item["width"], item["height"],
                            uuid=item.get("uuid", None), polling_rate=item.get("polling_rate", 1000))
                self.scene.addItem(clock)
                self.scene_items.append(clock)
            elif item["type"] == "controller":
                controller = DeskController(self, item["x"], item["y"], item["width"], item["height"],
                                            uuid=item.get("uuid", None), linked_snippet_uuid=item.get("linked_snippet_uuid", None))
                self.scene.addItem(controller)
                self.scene_items.append(controller)
        self.regenerate_hotkeys()

    def get_desk_configuration(self) -> list:
        """
        Get the configuration of the control desk
        :return: The configuration of the control desk
        """
        desk_configuration = []
        for item in self.scene_items:
            if isinstance(item, DeskButton):
                desk_configuration.append({
                    "type": "button",
                    "uuid": item.uuid,
                    "label": item.label,
                    "linked_controller_uuid": item.linked_controller_uuid,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.width,
                    "height": item.height,
                    "hotkey": item.hotkey,
                    "mode": item.mode,
                    "mode_duration": item.mode_duration
                })
            elif isinstance(item, DeskLabel):
                desk_configuration.append({
                    "type": "label",
                    "uuid": item.uuid,
                    "label": item.text,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.width,
                    "height": item.height
                })
            elif isinstance(item, DeskClock):
                desk_configuration.append({
                    "type": "clock",
                    "uuid": item.uuid,
                    "polling_rate": item.polling_rate,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.width,
                    "height": item.height
                })
            elif isinstance(item, DeskController):
                desk_configuration.append({
                    "type": "controller",
                    "uuid": item.uuid,
                    "linked_snippet_uuid": item.linked_snippet_uuid,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.width,
                    "height": item.height
                })
        return desk_configuration

    def get_item_with_uuid(self, uuid: str) -> object | None:
        """
        Get the item with the given UUID
        :param uuid: The UUID of the item to get
        :return: The item with the given UUID
        """
        for item in self.scene_items:
            if item.uuid == uuid:
                return item
        return None

    def regenerate_hotkeys(self) -> None:
        """
        (Re)generates the hotkeys for the buttons
        """
        for hotkey in self.available_hotkeys:
            hotkey.activated.disconnect()
            hotkey.deleteLater()
        self.available_hotkeys.clear()
        for item in self.scene_items:
            if not hasattr(item, "hotkey"):
                continue
            if not item.hotkey:
                continue
            shortcut = QShortcut(QKeySequence(item.hotkey), self)
            shortcut.activated.connect(item.clicked)
            self.available_hotkeys.append(shortcut)

    def has_active_item(self) -> bool:
        """
        Check if the control desk has at least one active item.
        :return: True if the control desk has at least one active item, false otherwise
        """
        for item in self.scene_items:
            if isinstance(item, DeskButton):
                if item.pressed:
                    return True
        return False

    def disable_all_items(self) -> None:
        """
        Disable all active control desk items.
        :return: None
        """
        for item in self.scene_items:
            if isinstance(item, DeskButton):
                if item.pressed:
                    item.clicked()

    def link_desk_item(self, target_type: str) -> None:
        """
        Activate linking mode for a specific item type.
        :param target_type: The type of item to link to (e.g. "controller", "button")
        :return: None
        """
        self.is_linking = target_type
        self.window.statusBar().showMessage(f"Linking mode activated. Click on a {target_type} to link it.")

    def complete_linking(self, result: str) -> None:
        """
        Called when a link target has been selected
        :param result: The result of the linking operation
        """
        self.is_linking = None
        self.linking_completed.emit(result)
        self.window.statusBar().clearMessage()
