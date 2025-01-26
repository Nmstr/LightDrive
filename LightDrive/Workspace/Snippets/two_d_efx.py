from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from dataclasses import dataclass, field
import uuid

@dataclass
class TwoDEfxData:
    uuid: str
    name: str
    type: str = field(default="two_d_efx", init=False)

class TwoDEfxManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

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
            two_d_efx_data = TwoDEfxData(two_2_efx_uuid, "New 2D Efx")
        efx_2d_entry.uuid = two_d_efx_data.uuid
        self.sm.available_snippets[two_d_efx_data.uuid] = two_d_efx_data

        efx_2d_entry.setText(0, self.sm.available_snippets[two_d_efx_data.uuid].name)
        self.sm.add_item(efx_2d_entry, parent)
