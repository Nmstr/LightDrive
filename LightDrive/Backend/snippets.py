from .output import OutputSnippet
from PySide6.QtCore import QTimer

class SequenceOutputSnippet(OutputSnippet):
    def __init__(self, window, sequence_uuid: str, start_index: int = 0, update_sequence_content_tree: bool = False) -> None:
        """
        Creates an output snippet specialized for sequences
        :param window: An instance of the class of the main window
        :param sequence_uuid: The UUID of the sequence
        :param start_index: The index to start at
        :param update_sequence_content_tree: Whether to update the sequence content tree (used for the editor)
        """
        super().__init__(window.dmx_output, {})
        self.window = window
        self.sequence_snippet = self.window.snippet_manager.available_snippets[sequence_uuid]
        self.current_index = start_index
        self.update_sequence_content_tree = update_sequence_content_tree

        self.timer = QTimer()
        self.timer.setInterval(self.sequence_snippet.scenes[self.current_index].get("duration"))
        self.timer.timeout.connect(self.next_scene)
        self.timer.start()

    def next_scene(self):
        """
        Goes to the next scene in the sequence
        :return: None
        """
        self.current_index += 1
        if self.current_index >= len(self.sequence_snippet.scenes):
            self.current_index = 0
        if self.update_sequence_content_tree:
            self.window.ui.sequence_content_tree.setCurrentItem(self.window.ui.sequence_content_tree.topLevelItem(self.current_index))
        new_values = self.window.snippet_manager.scene_manager.scene_construct_output_values(self.sequence_snippet.scenes[self.current_index].get("scene_uuid"))
        self.update_values(new_values)
        self.timer.setInterval(self.sequence_snippet.scenes[self.current_index].get("duration"))
