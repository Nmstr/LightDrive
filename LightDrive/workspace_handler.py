from data_structures import Workspace
from PySide6.QtCore import QObject, Slot
from urllib.parse import urlparse
import pathlib
import pickle

class WorkspaceHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.current_workspace_path = None

    @Slot()
    def new(self) -> None:
        self.root.workspace = Workspace()
        self.root.data_models.build_all()

    @Slot(str)
    def open(self, workspace_path: str) -> None:
        workspace_path = urlparse(workspace_path).path
        path = pathlib.Path(workspace_path)
        if not path.exists():
            return

        with open(str(path), "rb") as file:
            self.root.workspace = pickle.load(file)
            self.root.data_models.build_all()

        self.current_workspace_path = path

    @Slot()
    def save(self) -> None:
        if not self.current_workspace_path:
            return

        with open(str(self.current_workspace_path), "wb") as file:
            pickle.dump(self.root.workspace, file)

    @Slot(str)
    def save_as(self, workspace_path: str) -> None:
        workspace_path = urlparse(workspace_path).path
        path = pathlib.Path(workspace_path)

        with open(str(path), "wb") as file:
            pickle.dump(self.root.workspace, file)

        self.current_workspace_path = path
