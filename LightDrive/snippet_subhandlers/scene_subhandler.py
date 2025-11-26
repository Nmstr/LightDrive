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

        self.root.snippet_handler.loadScene.emit(snippet.uuid, snippet.name)

    @Slot(str, str)
    def add_fixture(self, snippet_uuid: str, fixture_uuid: str) -> None:
        print(snippet_uuid, fixture_uuid)
