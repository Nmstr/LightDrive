from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsItemGroup, QGraphicsPolygonItem, QApplication, QGraphicsPixmapItem, QMenu
from PySide6.QtGui import QPen, QPolygonF, QPixmap
from PySide6.QtCore import Qt, QPointF, QTimer, QElapsedTimer
import json
import os

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, track, x: float, y: float, diameter: int) -> None:
        """
        Create a keyframe
        :param track: The CueTimeline object
        :param x: The x position of the keyframe
        :param y: The y position of the keyframe
        :param diameter: The diameter of the keyframe
        :return: None
        """
        self.track = track
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            value.setY(round(value.y() / self.track.track.cue_timeline.track_y_size) * self.track.track.cue_timeline.track_y_size)
            if not QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
                tick_interval = self.track.track.cue_timeline.major_tick_interval / self.track.track.cue_timeline.num_minor_ticks
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
        self.body = QGraphicsRectItem(0, 0, 3, len(self.cue_timeline.cue_snippet.fixtures) * self.cue_timeline.track_y_size)
        self.body.setBrush(Qt.red)
        self.addToGroup(self.body)
        self.head = QGraphicsPolygonItem(QPolygonF([QPointF(-8.5, -20), QPointF(11.5, -20), QPointF(1.5, 0)]))
        self.head.setBrush(Qt.red)
        self.addToGroup(self.head)
        self.setPos(self.cue_timeline.track_y_size, 0)
        self.setZValue(1)

class FixtureSymbol(QGraphicsItemGroup):
    def __init__(self, cue_timeline, fixture_uuid: str) -> None:
        """
        Create a fixture symbol
        :param cue_timeline: The cue timeline
        :return: None
        """
        super().__init__()
        self.cue_timeline = cue_timeline
        self.fixture_uuid = fixture_uuid

        # Get the fixture data
        fixture_id = [item for item in self.cue_timeline.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0].get("id")
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture_id + ".json")) as f:
            fixture_data = json.load(f)

        # Add the fixture rect
        fixture_rect = QGraphicsRectItem(0, 0, self.cue_timeline.track_y_size, self.cue_timeline.track_y_size)
        fixture_rect.setBrush(Qt.darkGray)
        fixture_rect.setOpacity(0.25)
        self.addToGroup(fixture_rect)
        # Add the fixture icon
        pixmap = QPixmap(f"Assets/Icons/{fixture_data['light_type'].lower().replace(' ', '_')}.svg").scaled(self.cue_timeline.track_y_size, self.cue_timeline.track_y_size)
        fixture_pixmap_item = QGraphicsPixmapItem(pixmap)
        fixture_pixmap_item.setOpacity(0.25)
        self.addToGroup(fixture_pixmap_item)

        # Create context menu
        self.context_menu = QMenu()
        remove_fixture_action = self.context_menu.addAction("Remove Fixture")
        remove_fixture_action.triggered.connect(lambda: self.cue_timeline.window.snippet_manager.cue_manager.cue_remove_fixture(fixture_uuid=self.fixture_uuid))

    def contextMenuEvent(self, event):  # noqa: N802
        self.context_menu.exec(event.screenPos())

class MajorTrackBar(QGraphicsRectItem):
    def __init__(self, track) -> None:
        """
        Create a major track bar
        :param track: The cue timeline
        """
        super().__init__()
        self.track = track

        # Create the track
        self.setRect(0, 0, self.track.cue_timeline.track_length, self.track.cue_timeline.track_y_size)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.25)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            timeline_y_center = self.rect().center().y()
            keyframe = Keyframe(self, position.x() - self.track.cue_timeline.track_y_size, timeline_y_center + self.track.pos().y(), 10)
            self.track.cue_timeline.scene.addItem(keyframe)

class MinorTrackBar(QGraphicsRectItem):
    def __init__(self, track, channel_number: int) -> None:
        """
        Create a minor track bar
        :param track: The cue timeline
        :param channel_number: The channel number
        """
        super().__init__()
        self.track = track
        self.channel_number = channel_number

        # Create the track
        self.setRect(0, 0, self.track.cue_timeline.track_length, self.track.cue_timeline.track_y_size)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.5)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            timeline_y_center = self.rect().center().y()
            x_pos = position.x() - self.track.cue_timeline.track_y_size
            y_pos = timeline_y_center + self.track.pos().y() + (self.channel_number + 1) * self.track.cue_timeline.track_y_size
            keyframe = Keyframe(self, x_pos, y_pos, 10)
            self.track.cue_timeline.scene.addItem(keyframe)

class Track(QGraphicsItemGroup):
    def __init__(self, cue_timeline, fixture_uuid: str) -> None:
        super().__init__()
        self.cue_timeline = cue_timeline
        self.expanded = False

        # Create the fixture symbol
        self.fixture_symbol = FixtureSymbol(self.cue_timeline, fixture_uuid)
        self.addToGroup(self.fixture_symbol)
        # Create the track
        self.track_rect = MajorTrackBar(self)
        self.track_rect.setPos(self.cue_timeline.track_y_size, 0)
        self.addToGroup(self.track_rect)
        self.minor_tracks = []

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Propagate mousePressEvents to the items in the track
        :param event: The event
        :return: None
        """
        pass_on = True
        for item in self.childItems():
            if item.isUnderMouse():
                item.mousePressEvent(event)
                pass_on = False
        if pass_on:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Propagate mouseDoubleClickEvents to the items in the track
        :param event: The event
        :return: None
        """
        if not self.fixture_symbol.isUnderMouse():
            super().mouseDoubleClickEvent(event)
            return  # Stop here if fixture symbol is not under the mouse

        if self.expanded:  # If the already is expanded, collapse it
            for item in self.childItems():
                if isinstance(item, MinorTrackBar):
                    self.removeFromGroup(item)
                    self.cue_timeline.scene.removeItem(item)
            self.minor_tracks = []
            self.expanded = False
        else:  # If the track is not expanded, expand it
            self.expanded = True
            # Get the fixtures channels
            fixture_id = [item for item in self.cue_timeline.window.available_fixtures if item["fixture_uuid"] == self.fixture_symbol.fixture_uuid][0].get("id")
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture_id + ".json")) as f:
                fixture_data = json.load(f)
            channels = fixture_data["channels"]
            for channel_number, channel_data in channels.items():
                minor_track = MinorTrackBar(self, int(channel_number))
                minor_track.setPos(self.cue_timeline.track_y_size, self.pos().y() + 50 + int(channel_number) * 50)
                self.addToGroup(minor_track)
                self.minor_tracks.append(minor_track)
        self.cue_timeline.reposition_tracks()

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        """
        Propagate contextMenuEvents to the items in the track
        :param event: The event
        :return: None
        """
        if self.fixture_symbol.isUnderMouse():
            self.fixture_symbol.contextMenuEvent(event)
        else:
            super().contextMenuEvent(event)

class CueTimeline(QGraphicsView):
    def __init__(self, window: QMainWindow, cue_snippet) -> None:
        """
        Create the timeline object
        :param window: The main window
        :param: cue_snippet: The cue snippet
        """
        super().__init__(window)
        # Set some vars
        self.window = window
        self.cue_snippet = cue_snippet
        self.is_clicked = False
        self.major_tick_interval = 50
        self.num_minor_ticks = 3
        self.track_y_size = 50
        self.track_length = 2500
        self.top_buffer_zone_y = 50

        # Create and populate the scene
        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, self.track_length, self.window.ui.cue_timeline_frame.height())
        self.setScene(self.scene)
        if not fixture_uuids:  # If there are no fixtures, stop here
            return  # This prevents errors when opening empty cues
        self.tracks = []
        for fixture_uuid in self.cue_snippet.fixtures:
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
        track = Track(self, fixture_uuid)
        track.setPos(0, len(self.tracks) * self.track_y_size + self.top_buffer_zone_y)
        self.scene.addItem(track)
        self.tracks.append(track)

    def reposition_tracks(self) -> None:
        """
        Reposition the tracks in the timeline
        :return: None
        """
        next_y_pos = self.top_buffer_zone_y
        for i, track in enumerate(self.tracks):
            track.setPos(0, next_y_pos)
            next_y_pos += self.track_y_size
            for _ in track.minor_tracks:
                next_y_pos += self.track_y_size

    def add_ticks(self) -> None:
        """
        Add beats to the timeline
        :return: None
        """
        num_ticks = int(self.tracks[0].track_rect.rect().width() / self.major_tick_interval)
        major_tick_top = 10 + self.top_buffer_zone_y
        major_tick_bottom = -10 + self.top_buffer_zone_y
        minor_tick_top = 5 + self.top_buffer_zone_y
        minor_tick_bottom = -5 + self.top_buffer_zone_y
        pen = QPen(Qt.black)
        for i in range(num_ticks):
            x = i * self.major_tick_interval + self.track_y_size
            self.scene.addLine(x, major_tick_top, x, major_tick_bottom, pen)
            label = self.scene.addText(str(i + 1))
            label.setPos(x, -20 + self.top_buffer_zone_y)
            for j in range(1, self.num_minor_ticks + 1):  # Add minor ticks
                x_minor = x + j * self.major_tick_interval / (self.num_minor_ticks + 1)
                self.scene.addLine(x_minor, minor_tick_top, x_minor, minor_tick_bottom, pen)

    def add_playhead(self):
        """
        Adds the playhead to the timeline
        :return: None
        """
        playhead = Playhead(self)
        playhead.setPos(self.track_y_size, self.top_buffer_zone_y)
        self.scene.addItem(playhead)

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
        if event.button() == Qt.LeftButton:
            self.is_clicked = True
        super().mousePressEvent(event)

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
