from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter

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
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.resize_handle_size = 25
        self.resizing = False
        self.min_width = 50
        self.min_height = 50

        self.setPos(x, y)

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None, brush_color=Qt.lightGray) -> None:
        painter.setBrush(brush_color)
        painter.drawRect(self.boundingRect())

        # Draw resize handle in bottom right when not in live mode
        if not self.desk.window.live_mode:
            painter.setBrush(Qt.darkGray)
            painter.drawRect(
                self.width - self.resize_handle_size,
                self.height - self.resize_handle_size,
                self.resize_handle_size,
                self.resize_handle_size
            )

    def is_in_resize_handle(self, pos) -> bool:
        """
        Check if position is in the resize handle area
        """
        handle_rect = QRectF(
            self.width - self.resize_handle_size,
            self.height - self.resize_handle_size,
            self.resize_handle_size,
            self.resize_handle_size
        )
        return handle_rect.contains(pos)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self.desk.window.live_mode:
            super().mousePressEvent(event)
            return

        if self.is_in_resize_handle(event.pos()):  # If in resize handle, start resizing
            self.resizing = True
            self.setCursor(Qt.SizeFDiagCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self.resizing:
            # Calculate new dimensions
            new_width = max(self.min_width, event.pos().x())
            new_height = max(self.min_height, event.pos().y())

            # Ensure we don't exceed scene boundaries
            if self.x() + new_width > 1920:
                new_width = 1920 - self.x()
            if self.y() + new_height > 1080:
                new_height = 1080 - self.y()

            # Update dimensions and redraw
            if new_width != self.width or new_height != self.height:
                self.prepareGeometryChange()
                self.width = new_width
                self.height = new_height
                self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self.resizing:  # If resizing, stop resizing
            self.resizing = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            if self.desk.window.live_mode:  # Disable movement in live mode
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

