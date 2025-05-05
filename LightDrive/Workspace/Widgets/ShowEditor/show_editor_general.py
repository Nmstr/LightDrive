from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItemGroup, QGraphicsPolygonItem, QGraphicsLineItem, \
    QGraphicsTextItem
from PySide6.QtGui import QPen, QPolygonF
from PySide6.QtCore import Qt, QPointF

class TimingTickBar(QGraphicsItemGroup):
    def __init__(self, show_editor) -> None:
        """
        Create the timing tick bar
        :param show_editor: The show editor
        """
        super().__init__()
        self.show_editor = show_editor
        self.ticks = []
        self.labels = []

        self.body = QGraphicsRectItem(0, 0, self.show_editor.track_length, 50)
        self.body.setBrush(Qt.lightGray)
        self.setOpacity(0.5)
        self.addToGroup(self.body)

        self.update_ticks()

    def update_ticks(self) -> None:
        """
        Update the ticks, labels and body of the timing tick bar
        :return: None
        """
        for tick in self.ticks:
            self.removeFromGroup(tick)
            self.scene().removeItem(tick)
        self.ticks = []
        for label in self.labels:
            self.removeFromGroup(label)
            self.scene().removeItem(label)
        self.labels = []

        for i in range(0, self.show_editor.track_length, 100):
            x_pos = self.show_editor.virtual_frame_from_x_pos(i)
            tick = QGraphicsLineItem(x_pos, 0, x_pos, 50)
            tick.setPen(QPen(Qt.black, 1))
            self.ticks.append(tick)
            self.addToGroup(tick)
            label = QGraphicsTextItem(str(i / 100) + "s")
            label.setPos(x_pos, 0)
            self.labels.append(label)
            self.addToGroup(label)
        self.body.setRect(0, 0, self.show_editor.track_length * self.show_editor.zoom, 50)

class Playhead(QGraphicsItemGroup):
    def __init__(self) -> None:
        """
        Create a playhead
        :return: None
        """
        super().__init__()

        # Create the parts of the playhead
        self.body = QGraphicsRectItem(0, 0, 3, 100)
        self.body.setBrush(Qt.red)
        self.addToGroup(self.body)
        self.head = QGraphicsPolygonItem(QPolygonF([QPointF(-8.5, -20), QPointF(11.5, -20), QPointF(1.5, 0)]))
        self.head.setBrush(Qt.red)
        self.addToGroup(self.head)
        self.setZValue(1)

    def update_height(self, height: int) -> None:
        """
        Update the height of the playhead
        :param height: The new height of the playhead
        :return: None
        """
        self.body.setRect(0, 0, 3, height)
