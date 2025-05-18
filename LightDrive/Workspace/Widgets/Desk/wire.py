from .abstract_desk_item import AbstractDeskItem
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QPainterPath

class DeskWire(AbstractDeskItem):
    def __init__(self, desk, uuid: str, control_points: list[QPoint] = None) -> None:
        """
        Create a wire
        :param desk: The control desk
        :param uuid: The UUID of the wire
        """
        super().__init__(desk, 0, 0, 1920, 1080, uuid)
        self.desk = desk
        if not control_points:
            control_points = [QPoint(0, 0), QPoint(0, 0)]
        self.control_points = control_points

        self.setZValue(-100)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setPen(QPen(Qt.black, 2))
        path = QPainterPath()
        path.moveTo(self.control_points[0])
        for point in self.control_points[1:]:
            path.lineTo(point)
        painter.drawPath(path)
