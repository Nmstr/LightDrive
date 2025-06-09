from Workspace.Widgets.generic_item_view import GenericItemView
from Workspace.Widgets.Desk.ControllerProcessor.boolean_input_item import BooleanInputItem
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
        self.add_boolean_input_item()

    def add_boolean_input_item(self) -> None:
        """
        Add a boolean input item to the processor view
        """
        button = BooleanInputItem(self, 0, 0, 100, 100, uuid=str(uuid.uuid4()), input_state=1)
        self.scene.addItem(button)
        self.scene_items.append(button)

    def update_wires(self) -> None:
        # Placeholder for future implementation
        pass
