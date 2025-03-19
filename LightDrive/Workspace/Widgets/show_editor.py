from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsPolygonItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QPolygonF, QWheelEvent
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

        self.body = QGraphicsRectItem(0, 0, 2500, 50)
        self.body.setBrush(Qt.lightGray)
        self.setOpacity(0.5)
        self.addToGroup(self.body)

        self.update_ticks()

    def update_ticks(self) -> None:
        """
        Update the ticks and labels
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

        for i in range(0, 2500, 100):
            x_pos = self.show_editor.virtual_frame_from_x_pos(i)
            tick = QGraphicsLineItem(x_pos, 0, x_pos, 50)
            tick.setPen(QPen(Qt.black, 1))
            self.ticks.append(tick)
            self.addToGroup(tick)
            label = QGraphicsTextItem(str(i / 100) + "s")
            label.setPos(x_pos, 0)
            self.labels.append(label)
            self.addToGroup(label)

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
        self.setPos(100, 0)
        self.setZValue(1)

class AudioTrack(QGraphicsRectItem):
    def __init__(self) -> None:
        """
        Create an audio track
        """
        super().__init__()

        # Create the track
        self.setRect(0, 0, 2500, 100)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.25)

class ShowEditor(QGraphicsView):
    def __init__(self, window: QMainWindow, show_snippet) -> None:
        """
        Create the timeline object
        :param window: The main window
        :param: show_snippet: The cue snippet
        """
        super().__init__(window)
        self.window = window
        self.show_snippet = show_snippet
        self.zoom = 1.0
        self.is_clicked = False

        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, 2500, self.window.ui.show_editor_frame.height())
        self.setScene(self.scene)

        self.timing_tick_bar = TimingTickBar(self)
        self.scene.addItem(self.timing_tick_bar)
        self.track = AudioTrack()
        self.track.setY(100)
        self.scene.addItem(self.track)
        self.playhead = Playhead()
        self.playhead.setY(100)
        self.scene.addItem(self.playhead)

    def showEvent(self, event):  # noqa: N802
        """
        Sets the initially shown part of the scene to the top left side
        :param event: The event
        :return: None
        """
        super().showEvent(event)
        # This can not be in __init__ because the scrollbars are not initialized, yet
        # Thus it is required to be in showEvent after the scrollbars are fully initialized
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)

    def virtual_frame_from_x_pos(self, x_pos: int) -> int:
        """
        Converts the x position to a virtual frame
        :param x_pos: The x position
        :return: The virtual frame
        """
        return int(x_pos * self.zoom)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """
        Zoom in or out
        :param event: The event
        """
        if event.modifiers() == Qt.ControlModifier:
            # Zoom in or out
            if event.angleDelta().y() > 0:
                self.zoom += 0.1
            else:
                if self.zoom < 0.11:
                    return  # Dont allow negative zoom
                self.zoom -= 0.1
            self.timing_tick_bar.update_ticks()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        """
        Set the click state to true
        :param event: The event
        """
        if event.button() == Qt.LeftButton:
            self.is_clicked = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        """
        Set the click state to false
        :param event: The event
        """
        self.is_clicked = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        """
        Move the playhead
        :param event: The event
        """
        if self.is_clicked:
            position = self.mapToScene(event.pos())
            if position.x() < 0:
                return # Don't move the playhead off the left side
            self.playhead.setX(position.x())
        super().mouseMoveEvent(event)
