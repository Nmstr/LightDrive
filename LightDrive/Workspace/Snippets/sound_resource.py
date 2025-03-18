from PySide6.QtWidgets import QTreeWidgetItem, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from dataclasses import dataclass, field
from tinytag import TinyTag
import PySoundSphere
import tempfile
import shutil
import uuid
import os

@dataclass
class SoundResourceData:
    uuid: str
    name: str
    type: str = field(default="sound_resource", init=False)
    directory: str = field(default="root")

class SoundResourceManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager
        self.sr_tmp_dir = tempfile.mkdtemp()
        self.audio_player = PySoundSphere.AudioPlayer("sounddevice", sounddevice_blocksize=1024)

    def sound_resource_display(self, sound_resource_uuid: str) -> None:
        """
        Displays the sound resource editor for the given sound resource uuid
        :param sound_resource_uuid: The uuid of the sound resource to display
        :return: None
        """
        self._display_song_in_ui(sound_resource_uuid)

    def _display_song_in_ui(self, sound_resource_uuid: str) -> None:
        try:
            tag: TinyTag = TinyTag.get(os.path.join(self.sr_tmp_dir, sound_resource_uuid))
            title = tag.title
            duration = str(round(tag.duration, 2)) + " s"
            bitrate = str(tag.bitrate) + " kBits/s"
            samplerate = str(tag.samplerate) + " Hz"
        except FileNotFoundError:  # Most likely the song wasn't loaded/added yet
            title = "Unknown"
            duration = "0 s"
            bitrate = "0 kBits/s"
            samplerate = "0 Hz"
        self.sm.window.ui.sound_resource_title_edit_label.setText(title)
        self.sm.window.ui.sound_resource_duration_edit_label.setText(duration)
        self.sm.window.ui.sound_resource_bitrate_edit_label.setText(bitrate)
        self.sm.window.ui.sound_resource_samplerate_edit_label.setText(samplerate)

    def sound_resource_create(self, *, parent: QTreeWidgetItem = None, sound_resource_data: SoundResourceData = None) -> None:
        """
        Creates a sound resource in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param sound_resource_data: The data of the sound resource (only if importing)
        :return: None
        """
        sound_resource_entry = QTreeWidgetItem()
        sound_resource_entry.setIcon(0, QPixmap("Assets/Icons/sound_resource.svg"))
        if not sound_resource_data:
            sound_resource_uuid = str(uuid.uuid4())
            sound_resource_data = SoundResourceData(sound_resource_uuid, "New Sound Resource")
        sound_resource_entry.uuid = sound_resource_data.uuid
        self.sm.available_snippets[sound_resource_data.uuid] = sound_resource_data

        sound_resource_entry.setText(0, self.sm.available_snippets[sound_resource_data.uuid].name)
        self.sm.add_item(sound_resource_entry, parent)

    def sound_resource_rename(self, sound_resource_uuid: str = None, new_name: str = None) -> None:
        """
        Renames a sound_resource with the given uuid to the new name
        :param sound_resource_uuid: The uuid of the sound_resource to rename (if None, uses the currently selected snippets uuid)
        :param new_name: The new name of the sound_resource (if None, uses the name from ui.sound_resource_name_edit)
        :return: None
        """
        if not sound_resource_uuid:
            sound_resource_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.sound_resource_name_edit.text()
        sound_resource_snippet = self.sm.available_snippets.get(sound_resource_uuid)
        sound_resource_snippet.name = new_name
        sound_resource_entry = self.sm.find_snippet_entry_by_uuid(sound_resource_uuid)
        sound_resource_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def sound_resource_play_song(self, play: bool, sound_resource_uuid: str = None) -> None:
        if not sound_resource_uuid:
            sound_resource_uuid = self.sm.current_snippet.uuid
        if play:
            self.audio_player.load(os.path.join(self.sr_tmp_dir, sound_resource_uuid))
            self.audio_player.play()
        else:
            self.audio_player.stop()

    def sound_resource_load_song(self, sound_resource_uuid: str = None) -> None:
        if not sound_resource_uuid:
            sound_resource_uuid = self.sm.current_snippet.uuid
        song_path, _ = QFileDialog.getOpenFileName(self.sm.window, "Select a song", "", "Audio Files (*.mp3 *.wav)")
        if not os.path.exists(song_path):
            return  # Song doesnt exist
        shutil.copy(song_path, os.path.join(self.sr_tmp_dir, sound_resource_uuid))
        self._display_song_in_ui(sound_resource_uuid)
