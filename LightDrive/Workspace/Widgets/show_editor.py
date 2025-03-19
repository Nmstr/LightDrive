from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsPolygonItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtGui import QPen, QPolygonF, QWheelEvent, QPainter, QColor
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, QElapsedTimer
from tinytag import TinyTag
import numpy as np
import PySoundSphere
import librosa
import os

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

class AudioTrack(QGraphicsRectItem):
    def __init__(self, show_editor) -> None:
        """
        Create an audio track
        :param show_editor: The show editor
        """
        super().__init__()
        self.show_editor = show_editor

        # Create the track
        self.setRect(0, 0, self.show_editor.track_length, 100)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.25)

    def update_width(self) -> None:
        self.setRect(0, 0, self.show_editor.track_length * self.show_editor.zoom, 100)

class WaveformItem(QGraphicsItem):
    def __init__(self, waveform: np.ndarray, sample_rate: int, width: int, height: int, show_editor) -> None:
        super().__init__()
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.width = width
        self.height = height
        self.show_editor = show_editor

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        color = QColor(33, 58, 211)
        pen = QPen(color, 1)
        painter.setPen(pen)
        mid_y = self.height / 2
        step = len(self.waveform) / self.width
        for x in range(int(self.width)):
            start_idx = int(x * step)
            end_idx = int((x + 1) * step)
            segment = self.waveform[start_idx:end_idx]
            max_amplitude = np.max(np.abs(segment))
            y = mid_y - (max_amplitude * mid_y)
            painter.drawLine(int(x), int(mid_y), int(x), int(y))

    def update_width(self) -> None:
        self.width = self.show_editor.track_length * self.show_editor.zoom

class Markers(QGraphicsItemGroup):
    def __init__(self, show_editor, marker_times: np.ndarray, color, start_y: int, end_y: int) -> None:
        super().__init__()
        self.show_editor = show_editor
        self.marker_times = marker_times
        self.color = color
        self.start_y = start_y + 100
        self.end_y = end_y + 100
        self.markers = []

        self.update_markers()

    def update_markers(self) -> None:
        """
        Update the markers
        :return:
        """
        for marker in self.markers:
            self.removeFromGroup(marker)
            self.scene().removeItem(marker)
        self.markers = []

        for marker_time in self.marker_times:
            x_pos = self.show_editor.virtual_frame_from_x_pos(marker_time * 100)
            marker = QGraphicsLineItem(x_pos, self.start_y, x_pos, self.end_y)
            marker.setPen(QPen(self.color, 1))
            self.markers.append(marker)
            self.addToGroup(marker)

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

        sound_resource_uuid = show_snippet.sound_resource_uuid
        if sound_resource_uuid:
            song_path = os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid)
            tag: TinyTag = TinyTag.get(song_path)
            self.track_length = int(tag.duration * 100)
        else:
            self.track_length = 2500

        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, self.track_length, self.window.ui.show_editor_frame.height())
        self.setScene(self.scene)

        self.timing_tick_bar = TimingTickBar(self)
        self.scene.addItem(self.timing_tick_bar)
        self.track = AudioTrack(self)
        self.track.setY(50)
        self.scene.addItem(self.track)
        self.playhead = Playhead()
        self.playhead.setY(50)
        self.scene.addItem(self.playhead)

        self.play_timer = QTimer()
        self.play_elapsed_timer = QElapsedTimer()
        self.play_timer.timeout.connect(self.update_virtual_frame)
        self.start_frame = 0
        self.is_playing = False

        self.player = PySoundSphere.AudioPlayer("pygame")
        self.load_player()
        self.player.volume = 0.1

        self.waveform_item = None
        self.load_waveform()

        self.vary_beat_markers = None
        self.onset_markers = None
        self.beat_markers = None
        self.load_markers()

    def load_player(self):
        sound_resource_uuid = self.show_snippet.sound_resource_uuid
        if not sound_resource_uuid:
            return  # No sound resource set
        file_path = os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid)
        self.player.load(file_path)

    def load_waveform(self):
        sound_resource_uuid = self.show_snippet.sound_resource_uuid
        if not sound_resource_uuid:
            return  # No sound resource set
        file_path = os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid)

        if self.waveform_item:  # Remove old waveform
            self.scene.removeItem(self.waveform_item)
        self.waveform_item = None

        waveform, sample_rate = librosa.load(file_path, sr=None)
        self.waveform_item = WaveformItem(waveform, sample_rate, width=self.track_length, height=100, show_editor=self)
        self.waveform_item.setY(50)
        self.scene.addItem(self.waveform_item)

    def load_markers(self):
        sound_resource_uuid = self.show_snippet.sound_resource_uuid
        if not sound_resource_uuid:
            return  # No sound resource set
        file_path = os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid)

        if not self.vary_beat_markers:  # Remove old vary beat markers
            self.scene.removeItem(self.vary_beat_markers)
        self.vary_beat_markers = None
        if not self.onset_markers:  # Remove old onset markers
            self.scene.removeItem(self.onset_markers)
        self.onset_markers = None
        if self.beat_markers:  # Remove old beat markers
            self.scene.removeItem(self.beat_markers)
        self.beat_markers = None

        y, sr = librosa.load(file_path)

        vary_beat_color = Qt.yellow
        tempo_dynamic = librosa.feature.tempo(y=y, sr=sr, aggregate=None, std_bpm=4)
        _, vary_beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=tempo_dynamic)
        vary_beat_times = librosa.frames_to_time(vary_beat_frames, sr=sr)
        self.vary_beat_markers = Markers(self, vary_beat_times, vary_beat_color, 0, 16)
        self.scene.addItem(self.vary_beat_markers)

        onset_color = Qt.red
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        self.onset_markers = Markers(self, onset_times, onset_color, 17, 32)
        self.scene.addItem(self.onset_markers)

        beat_color = Qt.green
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        self.beat_markers = Markers(self, beat_times, beat_color, 33, 50)
        self.scene.addItem(self.beat_markers)

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

    def play(self):
        """
        Play the show
        :return: None
        """
        self.start_frame = self.virtual_frame_from_x_pos(int(self.playhead.x()))
        self.play_elapsed_timer.start()
        self.play_timer.start(10)  # Update every 10 ms
        self.is_playing = True
        self.player.play()
        self.player.position = self.virtual_frame_from_x_pos(int(self.playhead.x())) / 100

    def pause(self):
        """
        Pause the show
        :return: None
        """
        self.play_timer.stop()
        self.is_playing = False
        self.player.pause()

    def stop(self):
        """
        Stop the show
        :return: None
        """
        self.playhead.setX(0)
        self.play_timer.stop()
        self.is_playing = False
        self.player.stop()

    def update_virtual_frame(self) -> None:
        """
        Updates to the next virtual frame in the timeline while playback. Triggered by the play timer.
        :return: None
        """
        elapsed_time = self.play_elapsed_timer.elapsed() / 10
        virtual_frames = elapsed_time + self.start_frame
        self.playhead.setX(virtual_frames * self.zoom)

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
            self.setSceneRect(0, 0, self.track_length * self.zoom, self.window.ui.show_editor_frame.height())
            self.timing_tick_bar.update_ticks()
            self.track.update_width()
            self.waveform_item.update_width()
            self.vary_beat_markers.update_markers()
            self.onset_markers.update_markers()
            self.beat_markers.update_markers()
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
            vframe = self.virtual_frame_from_x_pos(int(position.x()))
            self.playhead.setX(position.x())
            self.player.position = vframe / 100
            if self.is_playing:
                self.start_frame = vframe
                self.play_elapsed_timer.restart()
        super().mouseMoveEvent(event)
