from snippet_subhandlers import scene_subhandler, sequence_subhandler
from data_structures import GenericSnippet, SceneSnippet, SequenceSnippet
from PySide6.QtCore import QObject, Slot, Signal

snippet_stack_mappings = {
    None: 0,
    SceneSnippet: 2,
    SequenceSnippet: 3,
}

class SnippetHandler(QObject):
    openSnippet = Signal(int)  # noqa: N815
    loadScene = Signal(str, str, bool, "QVariant")  # noqa: N815
    loadSequence = Signal(str, str, "QVariant")  # noqa: N815

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.scene_subhandler = scene_subhandler.SceneSubhandler(self.root, self)
        self.sequence_subhandler = sequence_subhandler.SequenceSubhandler(self.root, self)
        self.output_snippets = {}  # { snippet_uuid: output_snippet }

    @Slot(result=QObject)
    def get_scene_subhandler(self) -> scene_subhandler.SceneSubhandler:
        return self.scene_subhandler

    @Slot(result=QObject)
    def get_sequence_subhandler(self) -> sequence_subhandler.SequenceSubhandler:
        return self.sequence_subhandler

    @Slot(str)
    def remove_output_snippet(self, snippet_uuid: str) -> None:
        output_snippet = self.output_snippets.get(snippet_uuid)
        if not output_snippet:
            return
        self.root.output_manager.remove_snippet(output_snippet)
        self.output_snippets.pop(snippet_uuid)
        self.root.output_manager.tick_output()

    def get_snippet(self, snippet_uuid: str) -> GenericSnippet | None:
        for snippet in self.root.workspace.snippets:
            if snippet.uuid == snippet_uuid:
                return snippet
        return None

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
            case SequenceSnippet():
                stack_index = snippet_stack_mappings.get(type(target))
                self.openSnippet.emit(stack_index)
                self.sequence_subhandler.load(target)

    @Slot(str, str)
    def set_snippet_name(self, snippet_uuid: str, name: str) -> None:
        for snippet in self.root.workspace.snippets:
            if snippet.uuid == snippet_uuid:
                snippet.name = name
                self.root.data_models.build_snippet_model()
                break
