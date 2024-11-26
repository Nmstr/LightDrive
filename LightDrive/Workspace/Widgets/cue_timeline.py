from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, diameter: int) -> None:
        """
        Create a keyframe
        :param x: The x position of the keyframe
        :param y: The y position of the keyframe
        :param diameter: The diameter of the keyframe
        :return: None
        """
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

class CueTimeline(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the timeline object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)
        self.tracks = []
        for i in range(4):
            self.create_track()
        self.add_ticks()

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
        beat_interval = 50  # Distance between beats
        num_beats = int(self.tracks[0].rect().width() / beat_interval)
        pen = QPen(Qt.black)
        for i in range(num_beats):
            x = i * beat_interval
            tick = self.scene.addLine(x, -10, x, 10, pen)
            label = self.scene.addText(str(i + 1))
            label.setPos(x, -20)

    def add_keyframe(self, position) -> None:
        """
        Adds a keyframe onto a timeline
        :param position: The QPoint the object should be created at
        :return: None
        """
        for track in self.tracks:
            if track.rect().contains(position.x(), position.y()):
                timeline_y_center = track.rect().center().y()
                keyframe = Keyframe(position.x(), timeline_y_center, 10)
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
        super().mousePressEvent(event)
