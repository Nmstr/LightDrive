from .output import OutputSnippet
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsEllipseItem
from PySide6.QtGui import QPen
from PySide6.QtCore import QTimer, Qt

class ShowOutputSnippet(OutputSnippet):
    def __init__(self, window, show_uuid: str) -> None:
        """
        Creates an output snippet specialized for shows
        :param window: An instance of the class of the main window
        :param show_uuid: The UUID of the show
        """
        super().__init__(window.dmx_output, {})
        self.window = window
        self.show_snippet = self.window.snippet_manager.available_snippets[show_uuid]
        self.frame = 0
        self._paused = False
        self.current_output_snippets = {}

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start()

    def next_frame(self) -> None:
        # Add new snippets
        for snippet_item_uuid, snippet_item_data in self.show_snippet.added_snippets.items():
            if snippet_item_data.get("frame", None) == self.frame:
                snippet = self.window.snippet_manager.available_snippets[snippet_item_data["snippet_uuid"]]
                match snippet.type:
                    case "scene":
                        scene_out_val = self.window.snippet_manager.scene_manager.scene_construct_output_values(snippet.uuid)
                        new_output_snippet = OutputSnippet(self.window.dmx_output, scene_out_val)
                    case "two_d_efx":
                        new_output_snippet = TwoDEfxOutputSnippet(self.window, snippet.uuid)
                    case "sequence":
                        new_output_snippet = SequenceOutputSnippet(self.window, snippet.uuid)
                    case _:
                        continue

                self.current_output_snippets[snippet_item_uuid] = {
                    "snippet": new_output_snippet,
                    "start_frame": snippet_item_data["frame"],
                    "end_frame": snippet_item_data["frame"] + snippet_item_data["length"]
                }

        # Remove old snippets
        for current_snippet_item_uuid, current_snippet_data in self.current_output_snippets.copy().items():
            if current_snippet_data["end_frame"] < self.frame:
                del self.current_output_snippets[current_snippet_item_uuid]

        # Get all output values
        all_outputs = []
        for snippet_item_uuid, snippet_item_data in self.current_output_snippets.items():
            all_outputs.append(snippet_item_data["snippet"].values)

        # Construct the combined output values
        new_values = {}
        for output_dict in all_outputs:
            for universe_uuid, universe_data in output_dict.items():
                if universe_uuid not in new_values:
                    new_values[universe_uuid] = universe_data
                else:
                    new_values[universe_uuid].update(universe_data)

        # Update the output values
        self.update_values(new_values)
        if not self._paused:
            self.frame += 1

    def set_frame(self, frame: int) -> None:
        """
        Sets the frame of the show
        :param frame: The frame to set
        :return: None
        """
        self.frame = frame
        # Remove all running snippets
        for current_snippet_item_uuid in self.current_output_snippets.copy():
            del self.current_output_snippets[current_snippet_item_uuid]

    def pause(self) -> None:
        """
        Pauses the show
        :return: None
        """
        self._paused = True
        for output_snippet in self.current_output_snippets.values():
            try:
                output_snippet["snippet"].pause()
            except AttributeError:  # Not all snippets have a pause method (e.g. scenes)
                pass

    def unpause(self) -> None:
        """
        Unpauses the show
        :return: None
        """
        self._paused = False
        for output_snippet in self.current_output_snippets.values():
            try:
                output_snippet["snippet"].unpause()
            except AttributeError:  # see above
                pass

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
        self._paused = False

        self._time_till_next_scene = self.sequence_snippet.scenes[self.current_index].get("duration")
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.subtract_time)
        self.timer.start()

    def subtract_time(self) -> None:
        """
        Subtracts time from the time until the next scene
        :return: None
        """
        if self._paused:
            return
        self._time_till_next_scene -= 10
        if self._time_till_next_scene <= 0:
            self.next_scene()

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
        self._time_till_next_scene = self.sequence_snippet.scenes[self.current_index].get("duration")

    def pause(self) -> None:
        """
        Pauses the sequence
        :return: None
        """
        self._paused = True
        self.timer.stop()

    def unpause(self) -> None:
        """
        Unpauses the sequence
        :return: None
        """
        self._paused = False
        self.timer.start()

class TwoDEfxOutputSnippet(OutputSnippet):
    def __init__(self, window, two_d_efx_uuid: str) -> None:
        """
        Creates an output snippet specialized for 2D EFX
        :param window: An instance of the class of the main window
        :param two_d_efx_uuid: The UUID of the 2D EFX
        """
        super().__init__(window.dmx_output, {})
        self.window = window
        self.two_d_efx_snippet = self.window.snippet_manager.available_snippets[two_d_efx_uuid]
        self._paused = False

        self.internal_graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(window)
        self.internal_graphics_view.setSceneRect(0, 0, 511, 511)
        self.internal_graphics_view.setScene(self.scene)

        self.path = None
        self.tracer_dot = QGraphicsEllipseItem(0, 0, 20, 20)
        self.tracer_dot.setBrush(Qt.red)
        self.tracer_dot.setZValue(1)
        self.scene.addItem(self.tracer_dot)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.angle = 0

        self.update_path()

    def update_path(self) -> None:
        """
        Updates the path of the 2d efx
        :return: None
        """
        if self.path:
            self.scene.removeItem(self.path)
        painter_path = self.window.snippet_manager.two_d_efx_manager.two_d_efx_calculate_painter_path(self.two_d_efx_snippet.uuid)
        if painter_path:
            self.path = QGraphicsPathItem(painter_path)
            self.path.setPen(QPen(Qt.white, 2))
            self.scene.addItem(self.path)
            self.timer.start(8)

    def next_frame(self):
        """
        Goes to the next frame in the 2D EFX
        :return: None
        """
        if self._paused:
            return
        if self.path:
            length = self.path.path().length()
            increment = length / (self.two_d_efx_snippet.duration / 8)
            if self.two_d_efx_snippet.direction == "Backward":
                increment = -increment
            point = self.path.path().pointAtPercent((self.angle % length) / length)
            self.tracer_dot.setPos(point.x() - 10, point.y() - 10)
            self.angle += increment
            x_value = min(max(round(point.x() / 2), 0), 255)
            y_value = min(max(round(point.y() / 2), 0), 255)
            output = {}
            for fixture_uuid, mapping in self.two_d_efx_snippet.fixture_mappings.items():
                fixture = next((f for f in self.window.available_fixtures if f["fixture_uuid"] == fixture_uuid), None)
                if not fixture_uuid:
                    continue
                universe_uuid = fixture["universe"]
                fixture_address = fixture["address"]

                if not output.get(universe_uuid):
                    output[universe_uuid] = {}
                for channel, association in mapping.items():
                    if association == "X":
                        output[universe_uuid][int(channel) + fixture_address] = x_value
                    elif association == "Y":
                        output[universe_uuid][int(channel) + fixture_address] = y_value
            self.update_values(output)

    def pause(self) -> None:
        """
        Pauses the 2D EFX
        :return: None
        """
        self._paused = True

    def unpause(self) -> None:
        """
        Unpauses the 2D EFX
        :return: None
        """
        self._paused = False
