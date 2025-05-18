from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItem

class AbstractDeskItem(QGraphicsItem):
    def __init__(self, desk, x: int, y: int, width: int, height: int, uuid: str) -> None:
        """
        Create an abstract desk item
        :param desk: The control desk
        :param x: The x position of the abstract desk item
        :param y: The y position of the abstract desk item
        :param width: The width of the abstract desk item
        :param height: The height of the abstract desk item
        :param uuid: The uuid of the abstract desk item
        """
        super().__init__()
        self.desk = desk
        self.width = width
        self.height = height
        self.uuid = uuid

        self.setPos(x, y)

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, self.width, self.height)

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            if self.desk.window.live_mode or self.desk.is_linking:  # Disable movement in live mode or linking mode
                value.setX(self.x())
                value.setY(self.y())
                return super().itemChange(change, value)
            # Check if the item is within the bounds of the scene
            if value.x() < 0:
                value.setX(0)
            if value.y() < 0:
                value.setY(0)
            if value.x() + self.width > 1920:
                value.setX(1920 - self.width)
            if value.y() + self.height > 1080:
                value.setY(1080 - self.height)

        return super().itemChange(change, value)
