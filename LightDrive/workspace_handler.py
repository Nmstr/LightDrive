from data_structures import Workspace
from PySide6.QtCore import QObject, Slot, Signal
from urllib.parse import urlparse
import pathlib
import pickle

class WorkspaceHandler(QObject):
    promptSaveAs = Signal()  # noqa: N815

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.current_workspace_path = None

    @Slot()
    def new(self) -> None:
        self.current_workspace_path = None
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
            self.root.output_manager.build_output_universes()

            from data_structures import DeskButton, DeskFader, DeskKnob, DeskLabel, DeskClock, DeskSubdesk, DeskSnippetOutput
            self.root.workspace.desk_items.append(DeskButton("Button", x=100, y=100))
            self.root.workspace.desk_items.append(DeskFader("Fader", x=250, y=100))
            self.root.workspace.desk_items.append(DeskKnob("Knob", x=350, y=100))
            self.root.workspace.desk_items.append(DeskLabel("Label", x=100, y=50))
            self.root.workspace.desk_items.append(DeskClock("Clock", x=250, y=50))
            self.root.workspace.desk_items.append(DeskSubdesk("Subdesk", x=100, y=250))
            self.root.workspace.desk_items.append(DeskSnippetOutput("Snippet Output", x=400, y=250))
            self.root.desk_handler.desk_content_model.update()

        self.current_workspace_path = path

    @Slot()
    def save(self) -> None:
        if not self.current_workspace_path:
            self.promptSaveAs.emit()
            return  # Start save as if no path is set

        with open(str(self.current_workspace_path), "wb") as file:
            pickle.dump(self.root.workspace, file)

    @Slot(str)
    def save_as(self, workspace_path: str) -> None:
        workspace_path = urlparse(workspace_path).path
        path = pathlib.Path(workspace_path)

        with open(str(path), "wb") as file:
            pickle.dump(self.root.workspace, file)

        self.current_workspace_path = path
