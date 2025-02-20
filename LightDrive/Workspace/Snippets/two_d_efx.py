from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsLineItem, \
    QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QPixmap, QPen, QPainterPath
from PySide6.QtCore import Qt, QTimer
from dataclasses import dataclass, field
import uuid

@dataclass
class TwoDEfxData:
    uuid: str
    name: str
    type: str = field(default="two_d_efx", init=False)
    pattern: str
    width: int
    height: int
    x_offset: int
    y_offset: int

class TwoDEfxMovementDisplay(QGraphicsView):
    def __init__(self, window, two_d_efx_snippet: TwoDEfxData) -> None:
        super().__init__(window)
        self.window = window
        self.two_d_efx_snippet = two_d_efx_snippet

        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, 511, 511)
        self.setScene(self.scene)

        self.horizontal_line = QGraphicsLineItem(0, 255, 511, 255)
        self.scene.addItem(self.horizontal_line)
        self.vertical_line = QGraphicsLineItem(255, 511, 255, 0)
        self.scene.addItem(self.vertical_line)

        self.x_pos_text = QGraphicsTextItem("X: ---")
        self.x_pos_text.setPos(256, 0)
        self.scene.addItem(self.x_pos_text)
        self.y_pos_text = QGraphicsTextItem("Y: ---")
        self.y_pos_text.setPos(0, 256)
        self.scene.addItem(self.y_pos_text)

        self.path = None
        self.tracer_dot = QGraphicsEllipseItem(0, 0, 20, 20)
        self.tracer_dot.setBrush(Qt.red)
        self.tracer_dot.setZValue(1)
        self.scene.addItem(self.tracer_dot)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tracer_dot_position)
        self.angle = 0

        self.update_path()

    def update_path(self) -> None:
        """
        Updates the path of the 2d efx
        :return: None
        """
        if self.path:
            self.scene.removeItem(self.path)
        painter_path = None
        width = self.two_d_efx_snippet.width
        height = self.two_d_efx_snippet.height
        x_off = self.two_d_efx_snippet.x_offset
        y_off = self.two_d_efx_snippet.y_offset
        if self.two_d_efx_snippet.pattern == "Circle":
            painter_path = QPainterPath()
            painter_path.addEllipse(x_off, y_off, width, height)
        elif self.two_d_efx_snippet.pattern == "Square":
            painter_path = QPainterPath()
            painter_path.addRect(x_off, y_off, width, height)
        elif self.two_d_efx_snippet.pattern == "Triangle":
            painter_path = QPainterPath()
            painter_path.moveTo(width / 2 + x_off, y_off)
            painter_path.lineTo(width + x_off, height + y_off)
            painter_path.lineTo(x_off, height + y_off)
            painter_path.lineTo(width / 2 + x_off, y_off)
        elif self.two_d_efx_snippet.pattern == "Line":
            painter_path = QPainterPath()
            painter_path.moveTo(x_off, y_off)
            painter_path.lineTo(width + x_off, height + y_off)
        elif self.two_d_efx_snippet.pattern == "Eight":
            painter_path = QPainterPath()
            # TODO: Implement eight pattern
        if painter_path:
            self.path = QGraphicsPathItem(painter_path)
            self.path.setPen(QPen(Qt.white, 2))
            self.scene.addItem(self.path)
            self.timer.start(8)

    def update_tracer_dot_position(self) -> None:
        if self.path:
            length = self.path.path().length()
            point = self.path.path().pointAtPercent((self.angle % length) / length)
            self.tracer_dot.setPos(point.x() - 10, point.y() - 10)  # Adjust by half of the dot's width and height
            self.x_pos_text.setPlainText(f"X: {round(point.x())}")
            self.y_pos_text.setPlainText(f"Y: {round(point.y())}")
            self.angle += 1

class TwoDEfxManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager
        self.two_d_efx_movement_display = None

    def two_d_efx_display(self, two_d_efx_uuid: str = None) -> None:
        layout = clear_field(self.sm.window.ui.two_d_efx_movement_frame, QVBoxLayout, amount_left = 0)
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        self.two_d_efx_movement_display = TwoDEfxMovementDisplay(self.sm.window, two_d_efx_snippet)
        layout.addWidget(self.two_d_efx_movement_display)
        self.sm.window.ui.two_d_efx_width_spin.setValue(two_d_efx_snippet.width)
        self.sm.window.ui.two_d_efx_height_spin.setValue(two_d_efx_snippet.height)
        self.sm.window.ui.two_d_efx_x_offset_spin.setValue(two_d_efx_snippet.x_offset)
        self.sm.window.ui.two_d_efx_y_offset_spin.setValue(two_d_efx_snippet.y_offset)
        self.sm.window.ui.two_d_efx_pattern_combo.setCurrentText(two_d_efx_snippet.pattern)

    def two_d_efx_create(self, *, parent: QTreeWidgetItem = None, two_d_efx_data: TwoDEfxData = None) -> None:
        """
        Creates a 2d efx in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param two_d_efx_data: The data of the 2d efx (only if importing)
        :return: None
        """
        efx_2d_entry = QTreeWidgetItem()
        efx_2d_entry.setIcon(0, QPixmap("Assets/Icons/efx_2d.svg"))
        if not two_d_efx_data:
            two_2_efx_uuid = str(uuid.uuid4())
            two_d_efx_data = TwoDEfxData(two_2_efx_uuid, "New 2D Efx", "Circle", 512, 512, 0, 0)
        efx_2d_entry.uuid = two_d_efx_data.uuid
        self.sm.available_snippets[two_d_efx_data.uuid] = two_d_efx_data

        efx_2d_entry.setText(0, self.sm.available_snippets[two_d_efx_data.uuid].name)
        self.sm.add_item(efx_2d_entry, parent)

    def two_d_efx_rename(self, two_d_efx_uuid: str = None, new_name: str = None) -> None:
        """
        Renames the 2d efx with the given UUID to the new name
        :param two_d_efx_uuid: The UUID of the 2d efx to rename
        :param new_name: The new name of the 2d efx
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        if not new_name:
            new_name = self.sm.window.ui.two_d_efx_name_edit.text()
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        two_d_efx_snippet.name = new_name
        two_d_efx_entry = self.sm.find_snippet_entry_by_uuid(two_d_efx_uuid)
        two_d_efx_entry.setText(0, new_name)
        self.sm.window.ui.snippet_selector_tree.sortItems(0, Qt.AscendingOrder)

    def two_d_efx_change_pattern(self, pattern: str, two_d_efx_uuid: str = None) -> None:
        """
        Changes the pattern of the 2d efx with the given UUID to the new pattern
        :param pattern: The new pattern of the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to change the pattern of
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        self.sm.available_snippets[two_d_efx_uuid].pattern = pattern
        if self.two_d_efx_movement_display:
            self.two_d_efx_movement_display.update_path()

    def two_d_efx_change_width(self, width: int, two_d_efx_uuid: str = None) -> None:
        """
        Changes the width of the 2d efx with the given UUID to the new width
        :param width: The new width of the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to change the width of (if None, uses the current snippet)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        self.sm.available_snippets[two_d_efx_uuid].width = width
        if self.two_d_efx_movement_display:
            self.two_d_efx_movement_display.update_path()

    def two_d_efx_change_height(self, height: int = None, two_d_efx_uuid: str = None) -> None:
        """
        Changes the height of the 2d efx with the given UUID to the new height
        :param height: The new height of the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to change the height of (if None, uses the current snippet)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        self.sm.available_snippets[two_d_efx_uuid].height = height
        if self.two_d_efx_movement_display:
            self.two_d_efx_movement_display.update_path()

    def two_d_efx_change_x_offset(self,  x_offset: int, two_d_efx_uuid: str = None) -> None:
        """
        Changes the x offset of the 2d efx with the given UUID to the new x offset
        :param x_offset: The new x offset of the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to change the x offset of (if None, uses the current snippet)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        self.sm.available_snippets[two_d_efx_uuid].x_offset = x_offset
        if self.two_d_efx_movement_display:
            self.two_d_efx_movement_display.update_path()

    def two_d_efx_change_y_offset(self, y_offset: int, two_d_efx_uuid: str = None) -> None:
        """
        Changes the y offset of the 2d efx with the given UUID to the new y offset
        :param y_offset: The new y offset of the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to change the y offset of (if None, uses the current snippet)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        self.sm.available_snippets[two_d_efx_uuid].y_offset = y_offset
        if self.two_d_efx_movement_display:
            self.two_d_efx_movement_display.update_path()

    def two_d_efx_toggle_show(self) -> None:
        """
        Toggles whether the 2d efx is outputted over DMX
        :return: None
        """
