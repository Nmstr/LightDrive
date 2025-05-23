from .abstract_desk_item import AbstractDeskItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter

class ExtendedAbstractDeskItem(AbstractDeskItem):
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
        super().__init__(desk, x, y, width, height, uuid)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.resize_handle_size = 25
        self.resizing = False
        self.min_width = 50
        self.min_height = 50

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
        if self.desk.is_linking:
            # Get the own type of the item
            own_type = None
            for element in self.desk.get_desk_configuration():
                if element["uuid"] == self.uuid:
                    own_type = element["type"]
                    break
            # Own type matches the target type
            if own_type == self.desk.is_linking:
                self.desk.complete_linking(self.uuid)
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
            self.desk.update_wires()
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self.resizing:  # If resizing, stop resizing
            self.resizing = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
