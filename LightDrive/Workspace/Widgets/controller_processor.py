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

    def add_boolean_input_item(self) -> None:
        """
        Add a boolean input item to the processor view
        """
        button = BooleanInputItem(self, 0, 0, 100, 100, uuid=str(uuid.uuid4()), input_state=0)
        self.scene.addItem(button)
        self.scene_items.append(button)

    def load_processor_configuration(self, configuration: list) -> None:
        """
        Load the configuration of the controller processor.
        :param configuration: The configuration of the controller processor
        :return: None
        """
        for item in configuration:
            if item["type"] == "boolean_input":
                boolean_input = BooleanInputItem(self, item["x"], item["y"], item["width"], item["height"],
                                    uuid=item.get("uuid", None), input_state=item.get("input_state", 0))
                self.scene.addItem(boolean_input)
                self.scene_items.append(boolean_input)

    def get_processor_configuration(self) -> list:
        """
        Get the configuration of the controller processor.
        :return: The configuration of the controller processor
        """
        processor_configuration = []
        for item in self.scene_items:
            if isinstance(item, BooleanInputItem):
                processor_configuration.append({
                    "type": "boolean_input",
                    "uuid": item.uuid,
                    "x": item.x(),
                    "y": item.y(),
                    "width": item.width,
                    "height": item.height,
                    "input_state": item.input_state.value
                })
        return processor_configuration

    def update_wires(self) -> None:
        # Placeholder for future implementation
        pass
