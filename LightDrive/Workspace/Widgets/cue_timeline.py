from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsItemGroup, QGraphicsPolygonItem, QApplication, QGraphicsPixmapItem, QMenu, QGraphicsLineItem
from PySide6.QtGui import QPen, QPolygonF, QPixmap
from PySide6.QtCore import Qt, QPointF, QTimer, QElapsedTimer
import json
import os

class KeyframeLine(QGraphicsLineItem):
    def __init__(self, start_item, end_item):
        super().__init__()
        self.setPen(QPen(Qt.black, 2))
        start_pos = start_item.scenePos()
        end_pos = end_item.scenePos()
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, track, x: float, y: float, diameter: int, minor_track_number: int = 0) -> None:
        """
        Create a keyframe
        :param track: The CueTimeline object
        :param x: The x position of the keyframe
        :param y: The y position of the keyframe
        :param diameter: The diameter of the keyframe
        :param minor_track_number: The minor track the keyframe is on (0 if it is not on a minor track)
        :return: None
        """
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.track = track
        self.value = 127
        self.minor_track_number = minor_track_number
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(1)

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            # Keep y position within the track
            minor_track_offset = self.minor_track_number * self.track.cue_timeline.track_y_size
            if value.y() < self.track.pos().y() + minor_track_offset:
                value.setY(self.track.pos().y() + minor_track_offset)
            if value.y() > self.track.pos().y() + self.track.cue_timeline.track_y_size + minor_track_offset:
                value.setY(self.track.pos().y() + self.track.cue_timeline.track_y_size + minor_track_offset)
            self.value = (value.y() - self.track.pos().y() - minor_track_offset) / 50 * 255
            # Snap to the major ticks
            if not QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
                tick_interval = self.track.cue_timeline.major_tick_interval / self.track.cue_timeline.num_minor_ticks
                value.setX(round(value.x() / tick_interval) * tick_interval)
            # Update the lines
            if self.minor_track_number:  # Minor
                self.track.minor_tracks[self.minor_track_number - 1].update_lines()
            else:  # Major
                self.track.update_lines()

        return super().itemChange(change, value)

    def set_y_from_value(self):
        minor_track_offset = self.minor_track_number * self.track.cue_timeline.track_y_size
        self.setY(self.track.pos().y() + minor_track_offset + self.value / 255 * 50)

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

    def adjust_height(self) -> None:
        """
        Adjust the height of the playhead to match the number of tracks
        :return: None
        """
        new_height = 0
        for track in self.cue_timeline.tracks:
            new_height += self.cue_timeline.track_y_size
            if track.expanded:
                for _ in track.minor_tracks:
                    new_height += self.cue_timeline.track_y_size
        self.body.setRect(0, 0, 3, new_height)

class FixtureSymbol(QGraphicsItemGroup):
    def __init__(self, track, fixture_uuid: str) -> None:
        """
        Create a fixture symbol
        :param track: The track the fixture is on
        :return: None
        """
        super().__init__()
        self.track = track
        self.fixture_uuid = fixture_uuid

        # Get the fixture data
        fixture_id = [item for item in self.track.cue_timeline.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0].get("id")
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture_id + ".json")) as f:
            fixture_data = json.load(f)

        # Add the fixture rect
        fixture_rect = QGraphicsRectItem(0, 0, self.track.cue_timeline.track_y_size, self.track.cue_timeline.track_y_size)
        fixture_rect.setBrush(Qt.darkGray)
        fixture_rect.setOpacity(0.25)
        self.addToGroup(fixture_rect)
        # Add the fixture icon
        pixmap = QPixmap(f"Assets/Icons/{fixture_data['light_type'].lower().replace(' ', '_')}.svg").scaled(self.track.cue_timeline.track_y_size, self.track.cue_timeline.track_y_size)
        fixture_pixmap_item = QGraphicsPixmapItem(pixmap)
        fixture_pixmap_item.setOpacity(0.25)
        self.addToGroup(fixture_pixmap_item)

        # Create context menu
        self.context_menu = QMenu()
        remove_fixture_action = self.context_menu.addAction("Remove Fixture")
        remove_fixture_action.triggered.connect(lambda: self.track.cue_timeline.window.snippet_manager.cue_manager.cue_remove_fixture(fixture_uuid=self.fixture_uuid))

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        if self.track.expanded:
            self.track.collapse_track()
        else:
            self.track.expand_track()

    def contextMenuEvent(self, event):  # noqa: N802
        self.context_menu.exec(event.screenPos())

class MajorTrack(QGraphicsRectItem):
    def __init__(self, cue_timeline, fixture_uuid: str) -> None:
        """
        Create a major track bar
        :param cue_timeline: The cue timeline
        :param fixture_uuid: The UUID of the fixture associated with this track
        """
        super().__init__()
        self.cue_timeline = cue_timeline
        self.minor_tracks = []
        self.expanded = False
        self.keyframes = []
        self.lines = []

        # Create the track
        self.setRect(0, 0, self.cue_timeline.track_length, self.cue_timeline.track_y_size)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.25)
        self.fixture_symbol = FixtureSymbol(self, fixture_uuid)
        y_pos = len(self.cue_timeline.tracks) * self.cue_timeline.track_y_size + self.cue_timeline.top_buffer_zone_y
        self.fixture_symbol.setPos(0, y_pos)
        self.cue_timeline.scene.addItem(self.fixture_symbol)

        self.add_minor_tracks()

    def add_minor_tracks(self) -> None:
        """
        Adds the minor tracks to the track
        :return: None
        """
        # Get the fixtures channels
        fixture_id = [item for item in self.cue_timeline.window.available_fixtures if item["fixture_uuid"] == self.fixture_symbol.fixture_uuid][0].get("id")
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture_id + ".json")) as f:
            fixture_data = json.load(f)
        channels = fixture_data["channels"]
        # Create the minor tracks
        for channel_number, channel_data in channels.items():
            minor_track = MinorTrack(self, int(channel_number))
            minor_track.setPos(self.cue_timeline.track_y_size, self.pos().y() + 50 + int(channel_number) * 50)
            self.minor_tracks.append(minor_track)

    def expand_track(self) -> None:
        """
        Expand the track to show the minor tracks
        :return: None
        """
        if self.expanded:  # Don't expand the track if it is already expanded
            return
        for track in self.minor_tracks:  # Show tracks
            self.cue_timeline.scene.addItem(track)
            for keyframe in track.keyframes:  # Show keyframes
                self.cue_timeline.scene.addItem(keyframe)
        self.expanded = True
        self.cue_timeline.reposition_tracks()

    def collapse_track(self) -> None:
        """
        Collapse the track to hide the minor tracks
        :return: None
        """
        if not self.expanded:  # Don't collapse the track if it is already collapsed
            return
        for item in self.cue_timeline.scene.items():
            minor_track_to_remove = isinstance(item, MinorTrack) and item.track == self
            keyframe_to_remove = isinstance(item, Keyframe) and item.track == self and item.minor_track_number
            if minor_track_to_remove or keyframe_to_remove:
                self.cue_timeline.scene.removeItem(item)
        self.expanded = False
        self.cue_timeline.reposition_tracks()

    def add_keyframe(self, position) -> None:
        keyframe = Keyframe(self, 0, 0, 10)
        x_pos = position.x()
        y_pos = self.rect().center().y() + self.pos().y()
        keyframe.setPos(x_pos, y_pos)
        self.cue_timeline.scene.addItem(keyframe)
        self.keyframes.append(keyframe)
        self.update_lines()

    def update_lines(self):
        self.keyframes.sort(key=lambda kf: kf.x())
        for line in self.lines:
            self.cue_timeline.scene.removeItem(line)
            self.lines = []
        for i in range(len(self.keyframes) - 1):
            line = KeyframeLine(self.keyframes[i], self.keyframes[i + 1])
            self.cue_timeline.scene.addItem(line)
            self.lines.append(line)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            self.add_keyframe(position)

class MinorTrack(QGraphicsRectItem):
    def __init__(self, track, channel_number: int) -> None:
        """
        Create a minor track
        :param track: The cue timeline
        :param channel_number: The channel number
        """
        super().__init__()
        self.track = track
        self.track_number = channel_number + 1
        self.keyframes = []
        self.lines = []

        # Create the track
        self.setRect(0, 0, self.track.cue_timeline.track_length, self.track.cue_timeline.track_y_size)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.5)

    def add_keyframe(self, position) -> None:
        # Add a new keyframe
        keyframe = Keyframe(self.track, 0, 0, 10, minor_track_number=self.track_number)
        x_pos = position.x()
        y_pos = self.rect().center().y() + self.track.pos().y() + self.track_number * self.track.cue_timeline.track_y_size
        keyframe.setPos(x_pos, y_pos)
        self.track.cue_timeline.scene.addItem(keyframe)
        self.keyframes.append(keyframe)
        self.update_lines()

    def update_lines(self):
        self.keyframes.sort(key=lambda kf: kf.x())
        for line in self.lines:
            self.track.cue_timeline.scene.removeItem(line)
            self.lines = []
        if not self.track.expanded:
            return  # Don't draw lines if the track is collapsed
        for i in range(len(self.keyframes) - 1):
            line = KeyframeLine(self.keyframes[i], self.keyframes[i + 1])
            self.track.cue_timeline.scene.addItem(line)
            self.lines.append(line)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            self.add_keyframe(position)

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
        if not self.cue_snippet.fixtures:  # If there are no fixtures, stop here
            return  # This prevents errors when opening empty cues
        self.tracks = []
        for fixture_uuid in self.cue_snippet.fixtures:
            self.create_track(fixture_uuid)
        self.add_ticks()
        self.playhead = self.add_playhead()

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
        track = MajorTrack(self, fixture_uuid)
        track.setPos(self.track_y_size, len(self.tracks) * self.track_y_size + self.top_buffer_zone_y)
        self.scene.addItem(track)
        self.tracks.append(track)

    def reposition_tracks(self) -> None:
        """
        Reposition the tracks in the timeline
        :return: None
        """
        next_y_pos = self.top_buffer_zone_y
        # Move the tracks
        for i, track in enumerate(self.tracks):
            track.setY(next_y_pos)
            track.fixture_symbol.setY(next_y_pos)
            next_y_pos += self.track_y_size
            if track.expanded:
                for minor_track in track.minor_tracks:
                    minor_track.setY(next_y_pos)
                    next_y_pos += self.track_y_size
        # Move the keyframes
        for item in self.scene.items():
            if isinstance(item, Keyframe):
                item.set_y_from_value()
        # Update the lines
        for track in self.tracks:
            track.update_lines()
            for minor_track in track.minor_tracks:
                minor_track.update_lines()
        # Adjust playhead and scene height
        self.playhead.adjust_height()
        self.adjust_scene_height()

    def add_ticks(self) -> None:
        """
        Add beats to the timeline
        :return: None
        """
        num_ticks = int(self.tracks[0].rect().width() / self.major_tick_interval)
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

    def add_playhead(self) -> Playhead:
        """
        Adds the playhead to the timeline
        :return: None
        """
        playhead = Playhead(self)
        playhead.setPos(self.track_y_size, self.top_buffer_zone_y)
        self.scene.addItem(playhead)
        return playhead

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

    def adjust_scene_height(self) -> None:
        """
        Adjust the height of the scene to match the number of tracks
        :return: None
        """
        new_height = self.top_buffer_zone_y * 2
        for track in self.tracks:
            new_height += self.track_y_size
            if track.expanded:
                for _ in track.minor_tracks:
                    new_height += self.track_y_size
        if new_height < self.window.ui.cue_timeline_frame.height():
            new_height = self.window.ui.cue_timeline_frame.height()
        self.setSceneRect(0, 0, self.track_length, new_height)

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
