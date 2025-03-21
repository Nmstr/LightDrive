from Workspace.Widgets.Desk import DeskButton, DeskLabel, DeskClock
from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QShortcut, QKeySequence
import uuid

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
        self.setSceneRect(0, 0, 1920, 1080)
        self.scene_items = []
        self.available_hotkeys = []

    def add_btn(self) -> None:
        """
        Add a button to the control desk
        """
        button = DeskButton(self, 0, 0, 100, 100, button_uuid=str(uuid.uuid4()))
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
        label = DeskLabel(self, 0, 0, 150, 40, label_uuid=str(uuid.uuid4()), label_text="Label")
        self.scene.addItem(label)
        self.scene_items.append(label)

    def add_clock(self) -> None:
        """
        Add a clock to the control desk
        """
        clock = DeskClock(self, 0, 0, 150, 40, clock_uuid=str(uuid.uuid4()), polling_rate=1000)
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
                                    button_label=item.get("label", None), linked_snippet_uuid=item.get("linked_snippet_uuid", None),
                                    button_uuid=item.get("uuid", None), hotkey=item.get("hotkey", None), mode=item.get("mode", "toggle"),
                                    mode_duration=item.get("mode_duration", 0))
                self.scene.addItem(button)
                self.scene_items.append(button)
            elif item["type"] == "label":
                label = DeskLabel(self, item["x"], item["y"], item["width"], item["height"],
                                label_uuid=item.get("uuid", None), label_text=item.get("label", "Label"))
                self.scene.addItem(label)
                self.scene_items.append(label)
            elif item["type"] == "clock":
                clock = DeskClock(self, item["x"], item["y"], item["width"], item["height"],
                                clock_uuid=item.get("uuid", None), polling_rate=item.get("polling_rate", 1000))
                self.scene.addItem(clock)
                self.scene_items.append(clock)
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
                    "uuid": item.button_uuid,
                    "label": item.button_label,
                    "linked_snippet_uuid": item.linked_snippet_uuid,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.body.rect().width(),
                    "height": item.body.rect().height(),
                    "hotkey": item.hotkey,
                    "mode": item.mode,
                    "mode_duration": item.mode_duration
                })
            elif isinstance(item, DeskLabel):
                desk_configuration.append({
                    "type": "label",
                    "uuid": item.label_uuid,
                    "label": item.label_text,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.body.rect().width(),
                    "height": item.body.rect().height()
                })
            elif isinstance(item, DeskClock):
                desk_configuration.append({
                    "type": "clock",
                    "uuid": item.clock_uuid,
                    "polling_rate": item.polling_rate,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.body.rect().width(),
                    "height": item.body.rect().height()
                })
        return desk_configuration

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

    def disable_all_items(self) -> None:
        """
        Disable all active control desk items.
        :return: None
        """
        for item in self.scene_items:
            if isinstance(item, DeskButton):
                if item.pressed:
                    item.clicked()
