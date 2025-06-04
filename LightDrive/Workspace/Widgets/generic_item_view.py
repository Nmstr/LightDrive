from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene

class GenericItemView(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the generic item view
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1920, 1080)
        self.scene_items = []

    def get_item_with_uuid(self, item_uuid: str) -> object | None:
        """
        Get the item with the given UUID
        :param item_uuid: The UUID of the item to get
        :return: The item with the given UUID
        """
        for item in self.scene_items:
            if item.uuid == item_uuid:
                return item
        return None
