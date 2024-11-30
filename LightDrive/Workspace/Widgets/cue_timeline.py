from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsItemGroup, QGraphicsPolygonItem, QApplication
from PySide6.QtGui import QPen, QPolygonF
from PySide6.QtCore import Qt, QPointF

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, timeline, x: float, y: float, diameter: int) -> None:
        """
        Create a keyframe
        :param timeline: The CueTimeline object
        :param x: The x position of the keyframe
        :param y: The y position of the keyframe
        :param diameter: The diameter of the keyframe
        :return: None
        """
        self.timeline = timeline
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            value.setY(self.y())
            if not QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
                tick_interval = self.timeline.major_tick_interval / self.timeline.num_minor_ticks
                value.setX(round(value.x() / tick_interval) * tick_interval)
        return super().itemChange(change, value)

class Playhead(QGraphicsItemGroup):
    def __init__(self, cue_timeline) -> None:
        """
        Create a playhead
        :param cue_timeline: The cue timeline
        :return: None
        """
        super().__init__()
        self.cue_timeline = cue_timeline

        # Create the parts of the playhead
        self.body = QGraphicsRectItem(10, 0, 3, 200)
        self.body.setBrush(Qt.red)
        self.addToGroup(self.body)
        self.head = QGraphicsPolygonItem(QPolygonF([QPointF(1.5, -20), QPointF(21.5, -20), QPointF(11.5, 0)]))
        self.head.setBrush(Qt.red)
        self.addToGroup(self.head)

class CueTimeline(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the timeline object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.is_clicked = False
        self.major_tick_interval = 50
        self.num_minor_ticks = 3
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)
        self.tracks = []
        for i in range(4):
            self.create_track()
        self.add_ticks()
        self.add_playhead()

    def create_track(self) -> None:
        """
        Create a timeline
        :return: None
        """
        track_rect = QGraphicsRectItem(0, len(self.tracks) * 50, 2500, 50)
        track_rect.setBrush(Qt.lightGray)
        track_rect.setOpacity(0.25)
        self.scene.addItem(track_rect)
        self.tracks.append(track_rect)

    def add_ticks(self) -> None:
        """
        Add beats to the timeline
        :return: None
        """
        num_beats = int(self.tracks[0].rect().width() / self.major_tick_interval)
        pen = QPen(Qt.black)
        for i in range(num_beats):
            x = i * self.major_tick_interval
            self.scene.addLine(x, -10, x, 10, pen)
            label = self.scene.addText(str(i + 1))
            label.setPos(x, -20)
            for j in range(1, self.num_minor_ticks + 1):  # Add minor ticks
                x_minor = x + j * self.major_tick_interval / (self.num_minor_ticks + 1)
                self.scene.addLine(x_minor, -5, x_minor, 5, pen)

    def add_playhead(self):
        """
        Adds the playhead to the timeline
        :return: None
        """
        playhead = Playhead(self)
        self.scene.addItem(playhead)

    def add_keyframe(self, position) -> None:
        """
        Adds a keyframe onto a timeline
        :param position: The QPoint the object should be created at
        :return: None
        """
        for track in self.tracks:
            if track.rect().contains(position.x(), position.y()):
                timeline_y_center = track.rect().center().y()
                keyframe = Keyframe(self, position.x(), timeline_y_center, 10)
                self.scene.addItem(keyframe)
                break

    def mousePressEvent(self, event):  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            self.add_keyframe(position)
        elif event.button() == Qt.LeftButton:
            self.is_clicked = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        self.is_clicked = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self.is_clicked:
            # Move the playhead
            position = self.mapToScene(event.pos())
            if position.x() < 0:
                return # Don't move the playhead off the left side
            for item in self.scene.items():
                if isinstance(item, Playhead):
                    item.setPos(position.x()-11.5, item.y())
        super().mouseMoveEvent(event)
