from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsItemGroup, QGraphicsPolygonItem, QApplication, QGraphicsPixmapItem, QMenu
from PySide6.QtGui import QPen, QPolygonF, QPixmap
from PySide6.QtCore import Qt, QPointF, QTimer, QElapsedTimer
import json
import os

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
            value.setY(round(value.y() / self.timeline.track_y_size) * self.timeline.track_y_size)
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
        self.body = QGraphicsRectItem(0, 0, 3, len(self.cue_timeline.fixture_uuids) * self.cue_timeline.track_y_size)
        self.body.setBrush(Qt.red)
        self.addToGroup(self.body)
        self.head = QGraphicsPolygonItem(QPolygonF([QPointF(-8.5, -20), QPointF(11.5, -20), QPointF(1.5, 0)]))
        self.head.setBrush(Qt.red)
        self.addToGroup(self.head)
        self.setPos(self.cue_timeline.track_y_size, 0)
        self.setZValue(1)

class FixtureSymbol(QGraphicsItemGroup):
    def __init__(self, cue_timeline, fixture_data: list, fixture_uuid: str) -> None:
        """
        Create a fixture symbol
        :param cue_timeline: The cue timeline
        :param fixture_data: The fixture data
        :return: None
        """
        super().__init__()
        self.cue_timeline = cue_timeline
        self.fixture_data = fixture_data
        self.fixture_uuid = fixture_uuid

        # Add the fixture rect
        fixture_rect = QGraphicsRectItem(0, len(self.cue_timeline.tracks) * self.cue_timeline.track_y_size, self.cue_timeline.track_y_size, self.cue_timeline.track_y_size)
        fixture_rect.setBrush(Qt.darkGray)
        fixture_rect.setOpacity(0.25)
        self.addToGroup(fixture_rect)
        # Add the fixture icon
        pixmap = QPixmap(f"Assets/Icons/{self.fixture_data['light_type'].lower().replace(' ', '_')}.svg").scaled(self.cue_timeline.track_y_size, self.cue_timeline.track_y_size)
        fixture_pixmap_item = QGraphicsPixmapItem(pixmap)
        fixture_pixmap_item.setPos(0, len(self.cue_timeline.tracks) * self.cue_timeline.track_y_size)
        fixture_pixmap_item.setOpacity(0.25)
        self.addToGroup(fixture_pixmap_item)

        # Create context menu
        self.context_menu = QMenu()
        remove_fixture_action = self.context_menu.addAction("Remvoe Fixture")
        remove_fixture_action.triggered.connect(lambda: self.cue_timeline.window.snippet_manager.cue_remove_fixture(self.fixture_uuid))

    def contextMenuEvent(self, event):  # noqa: N802
        self.context_menu.exec(event.screenPos())

class CueTimeline(QGraphicsView):
    def __init__(self, window: QMainWindow, fixture_uuids: list) -> None:
        """
        Create the timeline object
        :param fixture_uuids: The list of fixture UUIDs in this cue
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.fixture_uuids = fixture_uuids
        self.is_clicked = False
        self.major_tick_interval = 50
        self.num_minor_ticks = 3
        self.track_y_size = 50
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)
        self.tracks = []
        for fixture_uuid in fixture_uuids:
            self.create_track(fixture_uuid)
        self.add_ticks()
        self.add_playhead()

        # Create timers and vars for playback
        self.play_timer = QTimer()
        self.play_elapsed_timer = QElapsedTimer()
        self.play_timer.timeout.connect(self.update_virtual_frame)
        self.start_frame = 0
        self.is_playing = False

    def create_track(self, fixture_uuid) -> None:
        """
        Create a timeline
        :param fixture_uuid: The UUID of the fixture associated with this track
        :return: None
        """
        # Get fixture data
        fixture_id = [item for item in self.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0].get("id")
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture_id + ".json")) as f:
            fixture_data = json.load(f)

        # Create the fixture symbol
        fixture_symbol = FixtureSymbol(self, fixture_data, fixture_uuid)
        self.scene.addItem(fixture_symbol)
        # Create the track
        track_rect = QGraphicsRectItem(self.track_y_size, len(self.tracks) * self.track_y_size, 2500, self.track_y_size)
        track_rect.setBrush(Qt.lightGray)
        track_rect.setOpacity(0.25)
        self.scene.addItem(track_rect)
        self.tracks.append(track_rect)

    def add_ticks(self) -> None:
        """
        Add beats to the timeline
        :return: None
        """
        num_ticks = int(self.tracks[0].rect().width() / self.major_tick_interval)
        pen = QPen(Qt.black)
        for i in range(num_ticks):
            x = i * self.major_tick_interval + self.track_y_size
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

    def play(self) -> None:
        """
        Start playback of the timeline
        :return: None
        """
        self.start_frame = self.current_virtual_frame
        self.play_elapsed_timer.start()
        self.play_timer.start(10)  # Update every 10 ms
        self.is_playing = True

    def pause(self) -> None:
        """
        Pause playback of the timeline
        :return: None
        """
        self.play_timer.stop()
        self.is_playing = False

    def stop(self) -> None:
        """
        Stop playback of the timeline
        :return: None
        """
        self.current_virtual_frame = 0
        self.play_timer.stop()
        self.is_playing = False

    def update_virtual_frame(self) -> None:
        """
        Updates to the next virtual frame in the timeline while playback. Triggered by the play timer.
        :return: None
        """
        # Calculate the virtual frame per second
        # bpm / 60 = beats per second; beats per second * 100 = virtual frames per second
        vfps = self.window.ui.cue_bpm_spin.value() / 60 * 100

        elapsed_time = self.play_elapsed_timer.elapsed() / 1000.0  # Elapsed time in seconds
        virtual_frames = elapsed_time * vfps + self.start_frame
        self.current_virtual_frame = virtual_frames

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
            position = self.mapToScene(event.pos())
            if position.x() < self.track_y_size:
                return # Don't move the playhead off the left side
            virtual_frame = round((position.x() - self.track_y_size) / self.major_tick_interval * 100)
            self.current_virtual_frame = virtual_frame
            if self.is_playing:
                self.start_frame = virtual_frame
                self.play_elapsed_timer.restart()
        super().mouseMoveEvent(event)

    @property
    def current_virtual_frame(self) -> int:
        """
        Get the current virtual frame
        :return: The current virtual frame
        """
        for item in self.scene.items():
            if isinstance(item, Playhead):
                return round((item.x() - self.track_y_size) / self.major_tick_interval * 100)
        return 0

    @current_virtual_frame.setter
    def current_virtual_frame(self, frame: int) -> None:
        """
        Set the current virtual frame
        :param frame: The frame to set as the current virtual frame
        :return: None
        """
        frame = round(frame)  # Account for floating point errors
        # Move the playhead
        for item in self.scene.items():
            if isinstance(item, Playhead):
                item.setPos(frame / 100 * self.major_tick_interval + self.track_y_size, item.y())
                break
        # Update the virtual frame label
        self.window.ui.cue_virtual_frame_label.setText(f"Virtual Frame: {frame}")
