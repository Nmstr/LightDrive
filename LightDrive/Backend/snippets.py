from .output import OutputSnippet
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsEllipseItem
from PySide6.QtGui import QPen, QPainterPath
from PySide6.QtCore import QTimer, Qt

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

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start()

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
        if self.path:
            length = self.path.path().length()
            point = self.path.path().pointAtPercent((self.angle % length) / length)
            self.tracer_dot.setPos(point.x() - 10, point.y() - 10)  # Adjust by half of the dot's width and height
            self.angle += 1
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

