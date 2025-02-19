from Functions.ui import clear_field
from PySide6.QtWidgets import QTreeWidgetItem, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
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
    def __init__(self, window, two_d_efx_data: TwoDEfxData) -> None:
        super().__init__(window)
        self.window = window
        self.two_d_efx_data = two_d_efx_data

        self.scene = QGraphicsScene(window)
        self.setSceneRect(0, 0, 511, 511)
        self.setScene(self.scene)

        self.horizontal_line = QGraphicsLineItem(0, 255, 511, 255)
        self.scene.addItem(self.horizontal_line)
        self.vertical_line = QGraphicsLineItem(255, 511, 255, 0)
        self.scene.addItem(self.vertical_line)

class TwoDEfxManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager
        self.two_d_efx_snippet = None

    def two_d_efx_display(self, two_d_efx_uuid: str = None) -> None:
        print(two_d_efx_uuid)
        layout = clear_field(self.sm.window.ui.two_d_efx_movement_frame, QVBoxLayout, amount_left = 0)
        two_d_efx_snippet = self.sm.available_snippets.get(two_d_efx_uuid)
        self.two_d_efx_movement_display = TwoDEfxMovementDisplay(self.sm.window, two_d_efx_snippet)
        layout.addWidget(self.two_d_efx_movement_display)

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
            two_d_efx_data = TwoDEfxData(two_2_efx_uuid, "New 2D Efx", "circle", 512, 512, 0, 0)
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

    def two_d_efx_toggle_show(self) -> None:
        """
        Toggles whether the 2d efx is outputted over DMX
        :return: None
        """
