from snippet_subhandlers import scene_subhandler
from data_structures import SceneSnippet
from PySide6.QtCore import QObject, Slot, Signal

snippet_stack_mappings = {
    None: 0,
    SceneSnippet: 2,
}

class SnippetHandler(QObject):
    openSnippet = Signal(int)  # noqa: N815
    loadScene = Signal(str, str, "QVariant")  # noqa: N815

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.scene_subhandler = scene_subhandler.SceneSubhandler(self.root)

    @Slot(result=QObject)
    def get_scene_subhandler(self) -> scene_subhandler.SceneSubhandler:
        return self.scene_subhandler

    @Slot(str)
    def open_snippet(self, uuid: str) -> None:
        for snippet in self.root.workspace.snippets:
            if snippet.uuid == uuid:
                target = snippet
                break
        else:
            return  # Snippet not found

        match target:
            case SceneSnippet():
                stack_index = snippet_stack_mappings.get(type(target))
                self.openSnippet.emit(stack_index)
                self.scene_subhandler.load(target)
