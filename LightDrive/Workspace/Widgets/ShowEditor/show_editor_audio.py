from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QPen, QPainter, QColor
from PySide6.QtCore import Qt, QRectF, Signal, QObject, QThread
import numpy as np
import librosa
import os

class AudioLoaderWorker(QObject):
    finished = Signal(np.ndarray, int)
    error = Signal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def run(self):
        try:
            y, sr = librosa.load(self.audio_path)
            self.finished.emit(y, sr)
        except Exception as e:
            self.error.emit(str(e))

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

        self.load_audio_background()

    def update_width(self) -> None:
        self.setRect(0, 0, self.show_editor.track_length * self.show_editor.zoom, 100)

    def load_audio_background(self) -> None:
        """
        Creates a thread to load the audio in the background and then loads the waveform and markers
        :return: None
        """
        sound_resource_uuid = self.show_editor.show_snippet.sound_resource_uuid
        if not sound_resource_uuid:
            return  # No sound resource set
        file_path = str(os.path.join(self.show_editor.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid))
        # Load the audio in a separate thread
        self.thread = QThread()
        self.worker = AudioLoaderWorker(file_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.show_editor.on_audio_loaded)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

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
        visible_rect = self.show_editor.mapToScene(self.show_editor.viewport().rect()).boundingRect()
        visible_start = max(0, int(visible_rect.left()))
        visible_end = min(int(self.width), int(visible_rect.right()))

        color = QColor(33, 58, 211)
        pen = QPen(color, 1)
        painter.setPen(pen)
        mid_y = self.height / 2
        step = len(self.waveform) / self.width
        for x in range(visible_start, visible_end):
            start_idx = int(x * step)
            end_idx = int((x + 1) * step)
            segment = self.waveform[start_idx:end_idx]
            max_amplitude = np.max(np.abs(segment))
            y = mid_y - (max_amplitude * mid_y)
            painter.drawLine(int(x), int(mid_y), int(x), int(y))

    def update_width(self) -> None:
        self.width = self.show_editor.track_length * self.show_editor.zoom

class Markers(QGraphicsItem):
    def __init__(self, show_editor, marker_times: np.ndarray, color, start_y: int, end_y: int) -> None:
        super().__init__()
        self.show_editor = show_editor
        self.marker_times = marker_times
        self.color = color
        self.start_y = start_y + 100
        self.end_y = end_y + 100
        self.width = self.show_editor.track_length
        self.height = 100

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        visible_rect = self.show_editor.mapToScene(self.show_editor.viewport().rect()).boundingRect()
        visible_start = max(0, visible_rect.left())
        visible_end = min(self.width, visible_rect.right())

        pen = QPen(self.color, 1)
        painter.setPen(pen)
        for marker_time in self.marker_times:
            x_pos = self.show_editor.virtual_frame_from_x_pos(marker_time * 100)
            if visible_start <= x_pos <= visible_end:
                painter.drawLine(x_pos, self.start_y, x_pos, self.end_y)

    def update_width(self) -> None:
        self.width = self.show_editor.track_length * self.show_editor.zoom

    def get_marker(self, time: float) -> float | None:
        """
        Check if the marker exists at the given time
        :param time: The time to check
        :return: The position of the marker if it exists, otherwise None
        """
        for marker_time in self.marker_times:
            if abs(time - marker_time) <= 0.1:
                return marker_time
        return None
