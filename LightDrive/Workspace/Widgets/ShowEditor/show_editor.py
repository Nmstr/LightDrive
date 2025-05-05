from Backend.snippets import ShowOutputSnippet
from Workspace.Widgets.ShowEditor.show_editor_general import TimingTickBar, Playhead
from Workspace.Widgets.ShowEditor.show_editor_snippets import SnippetTrack, SnippetItem
from Workspace.Widgets.ShowEditor.show_editor_audio import AudioTrack, WaveformItem, Markers
from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PySide6.QtGui import QWheelEvent, QPen
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from tinytag import TinyTag
import numpy as np
import PySoundSphere
import librosa
import uuid
import os

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
        self.output_snippet = ShowOutputSnippet(window, show_snippet.uuid)
        self.output_snippet.pause()

        sound_resource_uuid = show_snippet.sound_resource_uuid
        if sound_resource_uuid:
            song_path = os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid)
            tag: TinyTag = TinyTag.get(song_path)
            self.track_length = int(tag.duration * 100)
        else:
            self.track_length = 2500

        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, self.track_length, 1200)
        self.setScene(self.scene)

        self.timing_tick_bar = TimingTickBar(self)
        self.scene.addItem(self.timing_tick_bar)
        self.audiotrack = AudioTrack(self)
        self.audiotrack.setY(50)
        self.scene.addItem(self.audiotrack)
        self.playhead = Playhead()
        self.playhead.setY(50)
        self.playhead.update_height(1100)
        self.scene.addItem(self.playhead)

        self.snippets_tracks = []
        for i in range(10):
            snippet_track = SnippetTrack(self)
            snippet_track.setY((i + 1) * 100 + 50)
            self.scene.addItem(snippet_track)
            self.snippets_tracks.append(snippet_track)

        self.snippet_items = []
        for snippet_item_uuid, snippet_item_data in self.show_snippet.added_snippets.items():
            self.add_snippet(snippet_item_data["snippet_uuid"],
                             snippet_item_uuid,
                             snippet_item_data.get("track", 1),
                             snippet_item_data.get("frame", 0),
                             snippet_item_data.get("length", 250))

        self.play_timer = QTimer()
        self.play_elapsed_timer = QElapsedTimer()
        self.play_timer.timeout.connect(self.update_virtual_frame)
        self.start_frame = 0
        self.is_playing = False

        self.player = PySoundSphere.AudioPlayer("pygame")
        self.load_player()
        self.player.volume = 0.1

        self.waveform_item = None
        self.vary_beat_markers = None
        self.onset_markers = None
        self.beat_markers = None

        self.y = None
        self.sr = None

        self.extended_marker = QGraphicsLineItem(0, 100, 1, 1050)
        self.extended_marker.setPen(QPen(Qt.black, 1))
        self.extended_marker.hide()
        self.scene.addItem(self.extended_marker)

    def load_player(self) -> None:
        """
        Load the player with the sound resource
        :return: None
        """
        sound_resource_uuid = self.show_snippet.sound_resource_uuid
        if not sound_resource_uuid:
            return  # No sound resource set
        file_path = str(os.path.join(self.window.snippet_manager.sound_resource_manager.sr_tmp_dir, sound_resource_uuid))
        self.player.load(file_path)

    def on_audio_loaded(self, y: np.ndarray, sr: int) -> None:
        """
        Load the waveform and markers
        :param y: The audio data
        :param sr: The sample rate
        :return: None
        """
        self.y = y
        self.sr = sr
        self.load_waveform()
        self.load_markers()

    def load_waveform(self) -> None:
        """
        Load the waveform
        :return: None
        """
        if self.waveform_item:  # Remove old waveform
            self.scene.removeItem(self.waveform_item)
        self.waveform_item = None

        self.waveform_item = WaveformItem(self.y, self.sr, width=self.track_length, height=100, show_editor=self)
        self.waveform_item.setY(50)
        self.scene.addItem(self.waveform_item)

    def load_markers(self) -> None:
        """
        Load the markers
        :return: None
        """
        if not self.vary_beat_markers:  # Remove old vary beat markers
            self.scene.removeItem(self.vary_beat_markers)
        self.vary_beat_markers = None
        if not self.onset_markers:  # Remove old onset markers
            self.scene.removeItem(self.onset_markers)
        self.onset_markers = None
        if self.beat_markers:  # Remove old beat markers
            self.scene.removeItem(self.beat_markers)
        self.beat_markers = None

        vary_beat_color = Qt.yellow
        tempo_dynamic = librosa.feature.tempo(y=self.y, sr=self.sr, aggregate=None, std_bpm=4)
        _, vary_beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr, bpm=tempo_dynamic)
        vary_beat_times = librosa.frames_to_time(vary_beat_frames, sr=self.sr)
        self.vary_beat_markers = Markers(self, vary_beat_times, vary_beat_color, 0, 16)
        self.scene.addItem(self.vary_beat_markers)

        onset_color = Qt.red
        onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)
        self.onset_markers = Markers(self, onset_times, onset_color, 17, 32)
        self.scene.addItem(self.onset_markers)

        beat_color = Qt.green
        _, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
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
        self.output_snippet.unpause()

    def pause(self):
        """
        Pause the show
        :return: None
        """
        self.play_timer.stop()
        self.is_playing = False
        self.player.pause()
        self.output_snippet.pause()

    def stop(self):
        """
        Stop the show
        :return: None
        """
        self.playhead.setX(0)
        self.play_timer.stop()
        self.is_playing = False
        self.player.stop()
        self.output_snippet.pause()
        self.output_snippet.frame = 0

    def set_volume(self, volume: int) -> None:
        """
        Set the volume of the show
        :param volume: The volume
        :return: None
        """
        self.player.volume = volume / 100

    def add_snippet(self, snippet_uuid: str, snippet_item_uuid: str = None, track: int = 1, frame: int = 0, length: int = 250) -> None:
        if not snippet_item_uuid:
            snippet_item_uuid = str(uuid.uuid4())
        snippet_item = SnippetItem(self, snippet_item_uuid, snippet_uuid, track=track, frame=frame, length=length)
        self.scene.addItem(snippet_item)
        self.snippet_items.append(snippet_item)
        self.show_snippet.added_snippets[snippet_item_uuid] = {
                    "snippet_uuid": snippet_uuid,
                    "track": snippet_item.track,
                    "frame": snippet_item.frame,
                    "length": snippet_item.length
                }

    def remove_snippet_item(self, snippet_item_uuid: str) -> None:
        """
        Remove the snippet
        :param snippet_item_uuid: The uuid of the snippet item
        :return: None
        """
        if not snippet_item_uuid:
            return
        self.show_snippet.added_snippets.pop(snippet_item_uuid)
        for snippet_item in self.snippet_items:
            if snippet_item.uuid == snippet_item_uuid:
                self.scene.removeItem(snippet_item)
                self.snippet_items.remove(snippet_item)
                break

    def virtual_frame_from_x_pos(self, x_pos: int) -> int:
        """
        Converts the x position to a virtual frame
        :param x_pos: The x position
        :return: The virtual frame
        """
        return int(x_pos * self.zoom)

    def x_pos_from_virtual_frame(self, virtual_frame: int) -> int:
        """
        Converts the virtual frame to an x position
        :param virtual_frame:
        :return:
        """
        return int(virtual_frame / self.zoom)

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
            self.audiotrack.update_width()
            self.waveform_item.update_width()
            self.vary_beat_markers.update_width()
            self.onset_markers.update_width()
            self.beat_markers.update_width()
            for track in self.snippets_tracks:
                track.update_width()
            for snippet in self.snippet_items:
                snippet.update_width_position()
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
            self.output_snippet.set_frame(vframe)
            if self.is_playing:
                self.start_frame = vframe
                self.play_elapsed_timer.restart()
        super().mouseMoveEvent(event)

    def toggle_show(self, status: bool) -> None:
        """
        Toggle whether to show the show or not
        :param status: The status
        :return: None
        """
        if status:
            self.window.dmx_output.insert_snippet(self.output_snippet)
        else:
            self.window.dmx_output.remove_snippet(self.output_snippet)

