from Backend.snippets import TwoDEfxOutputSnippet
from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsLineItem, \
    QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QDialog, QDialogButtonBox, QTreeWidget, \
    QListWidgetItem, QFrame, QHBoxLayout, QLabel, QComboBox
from PySide6.QtGui import QPixmap, QPen, QPainterPath
from PySide6.QtCore import Qt, QTimer
from dataclasses import dataclass, field
import uuid
import json
import os

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
    fixture_mappings: dict = field(default_factory=dict)

class TwoDEfxAddFixtureDialog(QDialog):
    def __init__(self, window, fixture_mappings) -> None:
        self.window = window
        self.added_fixtures = list(fixture_mappings.keys())
        self.selected_fixtures = None
        super().__init__()
        self.setWindowTitle("LightDrive - Add Fixture to 2D Efx")

        layout = QVBoxLayout()
        self.fixture_selection_tree = QTreeWidget()
        self.fixture_selection_tree.setHeaderItem(QTreeWidgetItem(["Name", "Location", "ID", "UUID"]))
        self.fixture_selection_tree.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.fixture_selection_tree)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.load_fixtures()

    def load_fixtures(self) -> None:
        """
        Loads the fixtures and shows them in the fixture_selection_tree
        :return: None
        """
        for fixture in self.window.available_fixtures:
            if fixture.get("fixture_uuid") in self.added_fixtures:
                continue  # Don't show fixtures that are already added

            # Load fixture data
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture["id"] + ".json"), 'r') as f:
                fixture_data = json.load(f)

            # Add the item
            fixture_item = QTreeWidgetItem()
            fixture_item.extra_data = fixture
            fixture_item.setText(0, fixture["name"])
            fixture_item.setText(1, f"{fixture['universe']}>{fixture['address']}-{fixture['address'] + len(fixture_data["channels"]) - 1}")
            fixture_item.setText(2, fixture["id"])
            fixture_item.setText(3, fixture["fixture_uuid"])
            self.fixture_selection_tree.addTopLevelItem(fixture_item)

    def accept(self) -> None:
        """
        Accept the dialog to add the selected fixtures
        :return:
        """
        self.selected_fixtures = self.fixture_selection_tree.selectedItems()
        super().accept()

class TwoDEfxFixtureMappingDialog(QDialog):
    def __init__(self, window, fixture_uuid, two_d_efx_uuid) -> None:
        super().__init__()
        self.window = window
        self.fixture_uuid = fixture_uuid
        self.two_d_efx_snippet = self.window.snippet_manager.available_snippets.get(two_d_efx_uuid)
        self.result = []
        self.setWindowTitle("LightDrive - Edit Fixture Mapping")

        layout = QVBoxLayout()
        # Load fixture data
        fixture = [item for item in self.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0]
        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        with open(os.path.join(fixture_dir, fixture["id"] + ".json"), 'r') as f:
            fixture_data = json.load(f)
        self.combos = []
        for channel_number, channel_data in fixture_data["channels"].items():
            frame = QFrame()
            frame_layout = QHBoxLayout()
            frame.setLayout(frame_layout)
            frame_layout.addWidget(QLabel("Channel: " + channel_number))
            frame_layout.addWidget(QLabel("Name: " + channel_data["name"]))
            frame_layout.addWidget(QLabel("Mapping: "))
            combo = QComboBox()
            combo.addItem("None")
            combo.addItem("X")
            combo.addItem("Y")
            if channel_number in self.two_d_efx_snippet.fixture_mappings[self.fixture_uuid]:
                combo.setCurrentText(self.two_d_efx_snippet.fixture_mappings[self.fixture_uuid][channel_number])
            self.combos.append(combo)
            frame_layout.addWidget(combo)
            layout.addWidget(frame)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self) -> None:
        """
        Accept the dialog to modify the fixture mapping
        :return:
        """
        for combo in self.combos:
            self.result.append(combo.currentText())
        super().accept()

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
        painter_path = self.window.snippet_manager.two_d_efx_manager.two_d_efx_calculate_painter_path(self.two_d_efx_snippet.uuid)
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

    def two_d_efx_display(self, two_d_efx_uuid: str) -> None:
        """
        Loads the 2D Efx editor
        :param two_d_efx_uuid: The UUID of the 2d efx to load (if None, uses the current snippet)
        :return: None
        """
        layout = clear_field(self.sm.window.ui.two_d_efx_movement_frame, QVBoxLayout, amount_left = 0)
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        self.two_d_efx_movement_display = TwoDEfxMovementDisplay(self.sm.window, two_d_efx_snippet)
        layout.addWidget(self.two_d_efx_movement_display)
        self.sm.window.ui.two_d_efx_width_spin.setValue(two_d_efx_snippet.width)
        self.sm.window.ui.two_d_efx_height_spin.setValue(two_d_efx_snippet.height)
        self.sm.window.ui.two_d_efx_x_offset_spin.setValue(two_d_efx_snippet.x_offset)
        self.sm.window.ui.two_d_efx_y_offset_spin.setValue(two_d_efx_snippet.y_offset)
        self.sm.window.ui.two_d_efx_pattern_combo.setCurrentText(two_d_efx_snippet.pattern)
        self._two_d_efx_load_fixtures(two_d_efx_uuid)

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

    def _two_d_efx_load_fixtures(self, two_d_efx_uuid: str = None) -> None:
        """
        Loads the fixtures that are in a 2D Efx
        :param two_d_efx_uuid: The UUID of the 2d efx to load the fixtures of (if None, uses the current snippet)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)

        self.sm.window.ui.two_d_efx_fixture_list.clear()  # Remove current entries

        two_d_efx_fixtures = []
        for fixture_uuid in two_d_efx_snippet.fixture_mappings:
            matching_fixture = [item for item in self.sm.window.available_fixtures if item["fixture_uuid"] == fixture_uuid][0]
            two_d_efx_fixtures.append(matching_fixture)
        for fixture in two_d_efx_fixtures:  # Add the fixture to the QListWidget
            fixture_item = QListWidgetItem(fixture["name"])
            fixture_item.extra_data = fixture
            self.sm.window.ui.two_d_efx_fixture_list.addItem(fixture_item)

    def two_d_efx_add_fixture(self, two_d_efx_uuid: str = None, fixture_uuid: str = None) -> None:
        """
        Adds a fixture to the 2d efx
        :param two_d_efx_uuid: The UUID of the 2d efx to add the fixture to (if None, uses the current snippet)
        :param fixture_uuid: The UUID of the fixture to add (if None, prompts the user to select a fixture)
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        if not fixture_uuid:
            dlg = TwoDEfxAddFixtureDialog(self.sm.window, two_d_efx_snippet.fixture_mappings)
            if not dlg.exec():
                return
            for fixture in dlg.selected_fixtures:
                two_d_efx_snippet.fixture_mappings[fixture.extra_data["fixture_uuid"]] = {}
        else :
            two_d_efx_snippet.fixtures.append(fixture_uuid)
        self._two_d_efx_load_fixtures()

    def two_d_efx_remove_fixture(self, two_d_efx_uuid: str = None, fixture_uuid: str = None) -> None:
        """
        Removes a fixture from the 2d efx
        :return: None
        """
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        if not fixture_uuid:
            fixture_uuid = self.sm.window.ui.two_d_efx_fixture_list.selectedItems()[0].extra_data["fixture_uuid"]
        two_d_efx_uuid = self.sm.available_snippets.get(two_d_efx_uuid)
        two_d_efx_uuid.fixture_mappings.pop(fixture_uuid)
        self._two_d_efx_load_fixtures()

    def two_d_efx_calculate_painter_path(self, two_d_efx_uuid: str) -> QPainterPath:
        painter_path = QPainterPath()
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        width = two_d_efx_snippet.width
        height = two_d_efx_snippet.height
        x_off = two_d_efx_snippet.x_offset
        y_off = two_d_efx_snippet.y_offset
        if two_d_efx_snippet.pattern == "Circle":
            painter_path.addEllipse(x_off, y_off, width, height)
        elif two_d_efx_snippet.pattern == "Square":
            painter_path.addRect(x_off, y_off, width, height)
        elif two_d_efx_snippet.pattern == "Triangle":
            painter_path.moveTo(width / 2 + x_off, y_off)
            painter_path.lineTo(width + x_off, height + y_off)
            painter_path.lineTo(x_off, height + y_off)
            painter_path.lineTo(width / 2 + x_off, y_off)
        elif two_d_efx_snippet.pattern == "Line":
            painter_path.moveTo(x_off, y_off)
            painter_path.lineTo(width + x_off, height + y_off)
        elif two_d_efx_snippet.pattern == "Eight":
            painter_path.moveTo(x_off + width / 2, y_off)
            painter_path.cubicTo(x_off + width, y_off, x_off + width, y_off + height / 2, x_off + width / 2, y_off + height / 2)
            painter_path.cubicTo(x_off, y_off + height / 2, x_off, y_off + height, x_off + width / 2, y_off + height)
            painter_path.cubicTo(x_off + width, y_off + height, x_off + width, y_off + height / 2, x_off + width / 2, y_off + height / 2)
            painter_path.cubicTo(x_off, y_off + height / 2, x_off, y_off, x_off + width / 2, y_off)
        return painter_path

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
        if self.sm.current_display_snippet:
            self.sm.current_display_snippet.update_path()

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
        if self.sm.current_display_snippet:
            self.sm.current_display_snippet.update_path()

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
        if self.sm.current_display_snippet:
            self.sm.current_display_snippet.update_path()

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
        if self.sm.current_display_snippet:
            self.sm.current_display_snippet.update_path()

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
        if self.sm.current_display_snippet:
            self.sm.current_display_snippet.update_path()

    def two_d_efx_edit_fixture_mapping_wrapper(self, fixture_entry: QTreeWidgetItem) -> None:
        """
        This function just calls the actual function with the correct arguments
        It is needed to change the default arguments when calling the function from the UI
        :return: None
        """
        self.two_d_efx_edit_fixture_mapping(fixture_entry.extra_data["fixture_uuid"])

    def two_d_efx_edit_fixture_mapping(self, fixture_uuid: str = None, two_d_efx_uuid: str = None) -> None:
        if not fixture_uuid:
            fixture_uuid = self.sm.window.ui.two_d_efx_fixture_list.selectedItems()[0].extra_data["fixture_uuid"]
        if not two_d_efx_uuid:
            two_d_efx_uuid = self.sm.current_snippet.uuid
        dlg = TwoDEfxFixtureMappingDialog(self.sm.window, fixture_uuid, two_d_efx_uuid)
        if not dlg.exec():
            return
        print(dlg.result)
        for channel_number, mapping in enumerate(dlg.result):
            self.sm.available_snippets[two_d_efx_uuid].fixture_mappings[fixture_uuid][str(channel_number)] = mapping

    def two_d_efx_toggle_show(self) -> None:
        """
        Toggles whether the 2d efx is outputted over DMX
        :return: None
        """
        if self.sm.current_display_snippet is not None:  # Deactivate
            self.sm.window.dmx_output.remove_snippet(self.sm.current_display_snippet)
            self.sm.current_display_snippet = None

        if self.sm.window.ui.two_d_efx_show_btn.isChecked():  # Activate
            self.two_d_efx_movement_display.angle = 0
            self.sm.current_display_snippet = TwoDEfxOutputSnippet(self.sm.window, self.sm.current_snippet.uuid)
            self.sm.window.dmx_output.insert_snippet(self.sm.current_display_snippet)
