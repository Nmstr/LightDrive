from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QPixmap
from dataclasses import dataclass, field
import uuid

@dataclass
class ScriptData:
    uuid: str
    name: str
    type: str = field(default="script", init=False)

class ScriptManager:
    def __init__(self, snippet_manager) -> None:
        self.sm = snippet_manager

    def script_create(self, *, parent: QTreeWidgetItem = None, script_data: ScriptData = None) -> None:
        """
        Creates a script in the snippet selector tree
        :param parent: The parent QTreeWidgetITem for the new item (only if importing)
        :param script_data: The data of the script (only if importing)
        :return: None
        """
        script_entry = QTreeWidgetItem()
        script_entry.setIcon(0, QPixmap("Assets/Icons/script.svg"))
        if not script_data:
            script_uuid = str(uuid.uuid4())
            script_data = ScriptData(script_uuid, "New Script")
        script_entry.uuid = script_data.uuid
        self.sm.available_snippets[script_data.uuid] = script_data

        script_entry.setText(0, self.sm.available_snippets[script_data.uuid].name)
        self.sm.add_item(script_entry, parent)
