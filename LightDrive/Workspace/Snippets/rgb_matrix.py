from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from dataclasses import dataclass, field
import uuid

@dataclass
class RgbMatrixData:
    uuid: str
    name: str
    type: str = field(default="rgb_matrix", init=False)

class RgbMatrixManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def rgb_matrix_create(self, *, parent: QTreeWidgetItem = None, rgb_matrix_data: RgbMatrixData = None) -> None:
        """
        Creates a rgb matrix in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param rgb_matrix_data: The data of the rgb matrix (only if importing)
        :return: None
        """
        rgb_matrix_entry = QTreeWidgetItem()
        rgb_matrix_entry.setIcon(0, QPixmap("Assets/Icons/rgb_matrix.svg"))
        if not rgb_matrix_data:
            rgb_matrix_uuid = str(uuid.uuid4())
            rgb_matrix_data = RgbMatrixData(rgb_matrix_uuid, "New RGB Matrix")
        rgb_matrix_entry.uuid = rgb_matrix_data.uuid
        self.sm.available_snippets[rgb_matrix_data.uuid] = rgb_matrix_data

        rgb_matrix_entry.setText(0, self.sm.available_snippets[rgb_matrix_data.uuid].name)
        self.sm.add_item(rgb_matrix_entry, parent)
