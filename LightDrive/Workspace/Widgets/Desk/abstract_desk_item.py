from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup
from PySide6.QtCore import Qt

class AbstractDeskItem(QGraphicsItemGroup):
    def __init__(self, desk, x: int, y: int, width: int, height: int) -> None:
        """
        Create a label object
        :param desk: The control desk object
        :param x: The x position of the label
        :param y: The y position of the label
        :param width: The width of the label
        :param height: The height of the label
        """
        super().__init__()
        self.desk = desk
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.body = QGraphicsRectItem(0, 0, width, height)
        self.body.setBrush(Qt.lightGray)
        self.addToGroup(self.body)

        self.setPos(x, y)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        """
        Move the button
        """
        if self.desk.window.live_mode:
            return  # Disable movement in live mode
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        """
        Move the label back if it is out of bounds
        """
        if self.desk.window.live_mode:
            return  # Disable movement in live mode

        # Check button position and move if required
        width = self.body.rect().width()
        height = self.body.rect().height()
        if self.x() < 0:
            self.setPos(0, self.y())
        if self.y() < 0:
            self.setPos(self.x(), 0)
        if self.x() + width > 1920:
            self.setPos(1920 - width, self.y())
        if self.y() + height > 1080:
            self.setPos(self.x(), 1080 - height)
        super().mouseReleaseEvent(event)
