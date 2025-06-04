from ..extended_abstract_desk_item import ExtendedAbstractDeskItem

class InputItem(ExtendedAbstractDeskItem):
    def __init__(self, processor_view, x: int, y: int, width: int, height: int, uuid: str) -> None:
        """
        Create an input item for the controller processor
        :param processor_view: The processor view
        :param x: The x position of the input item
        :param y: The y position of the input item
        :param width: The width of the input item
        :param height: The height of the input item
        :param uuid: The uuid of the input item
        """
        super().__init__(processor_view, x, y, width, height, uuid)
