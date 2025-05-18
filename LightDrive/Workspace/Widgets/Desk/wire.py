from .abstract_desk_item import AbstractDeskItem
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QPainterPath

class DeskWire(AbstractDeskItem):
    def __init__(self, desk, uuid: str, start_item_uuid: str, end_item_uuid: str, control_points: list[QPoint] = None) -> None:
        """
        Create a wire
        :param desk: The control desk
        :param uuid: The UUID of the wire
        """
        super().__init__(desk, 0, 0, 1920, 1080, uuid)
        self.desk = desk
        self.start_item_uuid = start_item_uuid
        self.end_item_uuid = end_item_uuid
        if not control_points:
            control_points = []
        self.control_points = control_points

        self.setZValue(-100)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setPen(QPen(Qt.black, 2))
        path = QPainterPath()
        start_item = self.desk.get_item_with_uuid(self.start_item_uuid)
        path.moveTo(QPoint(start_item.x() + start_item.width / 2, start_item.y() + start_item.height / 2))
        for point in self.control_points:
            path.lineTo(point)
        end_item = self.desk.get_item_with_uuid(self.end_item_uuid)
        path.lineTo(QPoint(end_item.x() + end_item.width / 2, end_item.y() + end_item.height / 2))
        painter.drawPath(path)
