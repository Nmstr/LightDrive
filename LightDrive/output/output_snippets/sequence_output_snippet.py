from data_structures import SequenceSnippet
from output.output_snippets.generic_output_snippet import GenericOutputSnippet
from output.output_snippets.scene_output_snippet import SceneOutputSnippet
from PySide6.QtCore import QElapsedTimer
from dataclasses import dataclass
from typing import override

@dataclass
class SceneOutEntry:
    scene: SceneOutputSnippet
    starting_time: int
    ending_time: int

class SequenceOutputSnippet(GenericOutputSnippet):
    def __init__(self, root, priority: int, sequence_data: SequenceSnippet) -> None:
        self.sequence_data = sequence_data
        super().__init__(root, priority)
        self.scene_out_entries: list[SceneOutEntry] = self.build_scene_out_entries()

        self.timer = QElapsedTimer()
        self.timer.start()

    def build_scene_out_entries(self) -> list[SceneOutEntry]:
        entries = []
        scene_start_time = 0
        for scene_entry in self.sequence_data.scenes:
            scene_snippet = self._root.snippet_handler.get_snippet(scene_entry.scene_uuid)
            scene_output_snippet = SceneOutputSnippet(self._root, self.priority, scene_snippet)
            end_time = scene_start_time + scene_entry.fade_in + scene_entry.duration + scene_entry.fade_out
            entries.append(SceneOutEntry(scene_output_snippet, scene_start_time, end_time))
            scene_start_time = end_time
        return entries

    def _get_sequence_length(self) -> int:
        """
        Gets the length of the sequence in milliseconds.
        :return: The amount of milliseconds it takes for the sequence to complete.
        """
        return self.scene_out_entries[-1].ending_time

    @override
    def get_values(self, time: int = -1) -> dict[str, dict[int, int]]:
        if time == -1:  # Uses self-managed time
            time = self.timer.elapsed()

            sequence_length = self._get_sequence_length()
            while time >= sequence_length:  # Remove reruns from time
                time -= sequence_length

        # Get element with the biggest time that is smaller than the provided time
        scene_entry = max((entry for entry in self.scene_out_entries if entry.starting_time <= time),
                          key=lambda entry: entry.starting_time)

        if scene_entry == self.scene_out_entries[-1]:  # Last element, end time needs to be checked
            if scene_entry.ending_time < time:
                return {}  # Time is after sequence already ended

        return scene_entry.scene.get_values()
