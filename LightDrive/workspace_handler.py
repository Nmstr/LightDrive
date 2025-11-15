from PySide6.QtCore import QObject, Slot
import os

class WorkspaceHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot()
    def new(self) -> None:
        print("New")

    @Slot(str)
    def open(self, workspace_path: str) -> None:
        print("Open: ", workspace_path)
        if not os.path.isfile(workspace_path):
            return

    @Slot()
    def save(self) -> None:
        print("Save")

    @Slot(str)
    def save_as(self, workspace_path: str) -> None:
        print("Save as: ", workspace_path)
