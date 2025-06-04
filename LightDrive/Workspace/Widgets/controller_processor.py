from Workspace.Widgets.generic_item_view import GenericItemView
from Workspace.Widgets.Desk.ControllerProcessor.input_item import InputItem
from PySide6.QtWidgets import QMainWindow
import uuid

class ControllerProcessor(GenericItemView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the controller processor view
        :param window: The main window
        """
        super().__init__(window)
        self.is_linking = None
        self.add_input_item()

    def add_input_item(self) -> None:
        """
        Add an input item to the processor view
        """
        button = InputItem(self, 0, 0, 100, 100, uuid=str(uuid.uuid4()))
        self.scene.addItem(button)
        self.scene_items.append(button)

    def update_wires(self) -> None:
        # Placeholder for future implementation
        pass
