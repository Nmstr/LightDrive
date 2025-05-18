from .abstract_desk_item import AbstractDeskItem
from Functions.ui import clear_field
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, QFile, QPoint, QRectF
from PySide6.QtGui import QPainter, QPen, QPainterPath, QPainterPathStroker
from PySide6.QtUiTools import QUiLoader

class FixedPointDisplay(QWidget):
    def __init__(self, position: str, item_uuid: str) -> None:
        """
        Create a widget to display fixed points
        :param position: The position of the item (start or end)
        :param item_uuid: The UUID of the item
        """
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setText(f"{position} item UUID: {item_uuid}")
        layout.addWidget(self.label)
        self.setLayout(layout)

class ControlPointDisplay(QWidget):
    def __init__(self, config_dlg, control_point: list[int]) -> None:
        """
        Create a widget to display control points
        :param control_point: A control point
        """
        super().__init__()
        self.control_point = control_point
        self.config_dlg = config_dlg

        layout = QHBoxLayout()
        self.x_pos_label = QLabel(self)
        self.x_pos_label.setText("X: " + str(self.control_point[0]))
        layout.addWidget(self.x_pos_label)

        self.y_pos_label = QLabel(self)
        self.y_pos_label.setText("Y: " + str(self.control_point[1]))
        layout.addWidget(self.y_pos_label)

        self.move_frame = QFrame(self)
        layout.addWidget(self.move_frame)

        move_frame_layout = QVBoxLayout()
        self.move_up_btn = QPushButton("Up", self)
        self.move_up_btn.clicked.connect(self.move_up)
        move_frame_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("Down", self)
        self.move_down_btn.clicked.connect(self.move_down)
        move_frame_layout.addWidget(self.move_down_btn)

        self.move_frame.setLayout(move_frame_layout)
        self.setLayout(layout)

    def move_up(self) -> None:
        """
        Move the control point up
        """
        self.config_dlg.move_control_point(self.control_point, "up")

    def move_down(self) -> None:
        """
        Move the control point down
        """
        self.config_dlg.move_control_point(self.control_point, "down")

class DeskWireConfig(QDialog):
    def __init__(self, window, start_item_uuid: str, end_item_uuid: str, control_points: list[list[int]]) -> None:
        """
        Create a dialog for configuring a wire
        :param window: The main window
        :param start_item_uuid: The UUID of the start item
        :param end_item_uuid: The UUID of the end item
        :param control_points: The control points of the wire
        """
        super().__init__()
        self.window = window
        self.start_item_uuid = start_item_uuid
        self.end_item_uuid = end_item_uuid
        self.control_points = control_points

        self.setWindowTitle("LightDrive - Wire Properties")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/desk_wire_config.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        # Add control points
        self.refill_control_point_display()

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def refill_control_point_display(self) -> None:
        """
        Fill the control point display with the control points
        :return: None
        """
        # Empty the control points frame
        clear_field(self.ui.control_points_frame, QVBoxLayout, amount_left = 0)

        fixed_point_display_start = FixedPointDisplay("Start", self.start_item_uuid)
        self.ui.control_points_frame.layout().addWidget(fixed_point_display_start)
        for control_point in self.control_points:
            control_point_display = ControlPointDisplay(self, control_point)
            self.ui.control_points_frame.layout().addWidget(control_point_display)
        fixed_point_display_end = FixedPointDisplay("End", self.end_item_uuid)
        self.ui.control_points_frame.layout().addWidget(fixed_point_display_end)

    def move_control_point(self, point: list[int], direction: str) -> None:
        """
        Move a control point
        :param point: The control point to move
        :param direction: The direction to move the control point (up or down)
        """
        if direction == "up":
            current_index = self.control_points.index(point)
            self.control_points.remove(point)
            self.control_points.insert(current_index - 1, point)
        elif direction == "down":
            current_index = self.control_points.index(point)
            self.control_points.remove(point)
            self.control_points.insert(current_index + 1, point)
        self.refill_control_point_display()
        self.window.control_desk_view.update_wires()

class DeskWire(AbstractDeskItem):
    def __init__(self, desk, uuid: str, start_item_uuid: str, end_item_uuid: str, control_points: list[list[int]] = None) -> None:
        """
        Create a wire
        :param desk: The control desk
        :param uuid: The UUID of the wire
        :param start_item_uuid: The UUID of the start item
        :param end_item_uuid: The UUID of the end item
        :param control_points: The control points of the wire
        """
        super().__init__(desk, 0, 0, 1920, 1080, uuid)
        self.desk = desk
        self.start_item_uuid = start_item_uuid
        self.end_item_uuid = end_item_uuid
        if not control_points:
            control_points = []
        self.control_points = control_points

        self.setZValue(-100)

    def get_painter_path(self) -> QPainterPath:
        """
        Get the painter path for the wire
        """
        path = QPainterPath()
        # Go to start item
        start_item = self.desk.get_item_with_uuid(self.start_item_uuid)
        if not start_item:
            return path
        path.moveTo(QPoint(start_item.x() + start_item.width / 2, start_item.y() + start_item.height / 2))

        # Draw along control points
        for point in self.control_points:
            path.lineTo(QPoint(point[0], point[1]))

        # Draw to end item
        end_item = self.desk.get_item_with_uuid(self.end_item_uuid)
        if not end_item:
            return path
        path.lineTo(QPoint(end_item.x() + end_item.width / 2, end_item.y() + end_item.height / 2))

        return path

    def shape(self) -> QPainterPath:
        """
        Define the shape used for collision detection
        """
        path = self.get_painter_path()
        # Create a stroke with some padding for easier clicking
        stroker = QPainterPathStroker()
        stroker.setWidth(8)  # Adjust this value for click tolerance
        return stroker.createStroke(path)

    def boundingRect(self) -> QRectF:  # noqa: N802
        """
        Define the bounding rectangle for repainting
        """
        path = self.get_painter_path()
        # Path including a small margin
        return path.boundingRect().adjusted(-5, -5, 5, 5)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setPen(QPen(Qt.black, 2))
        path = self.get_painter_path()
        painter.drawPath(path)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the properties of the wire
        """
        if self.desk.window.live_mode or self.desk.is_linking:
            return  # Disable editing in live mode or when linking
        config_dlg = DeskWireConfig(window=self.desk.window, start_item_uuid=self.start_item_uuid, end_item_uuid=self.end_item_uuid, control_points=self.control_points)
        if config_dlg.exec():
            self.control_points = config_dlg.control_points
        super().mouseDoubleClickEvent(event)
