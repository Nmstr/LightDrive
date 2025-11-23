from data_structures import SceneSnippet
from PySide6.QtCore import QObject, Slot

class SceneSubhandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot()
    def add(self):
        self.root.workspace.snippets.append(SceneSnippet("Scene"))
        self.root.data_models.build_snippet_model()

    def load(self, snippet: SceneSnippet) -> None:
        if not snippet:
            return

        self.root.snippet_handler.loadScene.emit(snippet.name)

