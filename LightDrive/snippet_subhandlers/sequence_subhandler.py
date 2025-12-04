from data_structures import SequenceSnippet, SequenceSceneEntry, SceneSnippet
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QObject, Slot, Qt, QByteArray

class SequenceSubhandler(QObject):
    def __init__(self, root, snippet_handler):
        super().__init__()
        self.root = root
        self.snippet_handler = snippet_handler

    @Slot()
    def add(self):
        self.root.workspace.snippets.append(SequenceSnippet("New Sequence"))
        self.root.data_models.build_snippet_model()

    def load(self, snippet: SequenceSnippet) -> None:
        if not snippet:
            return

        sequence_model = QStandardItemModel()
        sequence_model.setItemRoleNames({
            Qt.DisplayRole: QByteArray(b"display"),
            Qt.UserRole: QByteArray(b"sceneUuid"),
            Qt.UserRole + 1: QByteArray(b"fadeIn"),
            Qt.UserRole + 2: QByteArray(b"duration"),
            Qt.UserRole + 3: QByteArray(b"fadeOut"),
        })
        # build model

        self.root.snippet_handler.loadSequence.emit(snippet.uuid, snippet.name, sequence_model)

    @Slot(str, str)
    def add_scene(self, sequence_uuid: str, scene_uuid: str) -> None:
        snippet = self.snippet_handler.get_snippet(sequence_uuid)
        if not snippet:
            return
        scene = self.snippet_handler.get_snippet(scene_uuid)
        if not scene:
            return
        if not isinstance(scene, SceneSnippet):
            return

        snippet.scenes.append(SequenceSceneEntry(scene_uuid))
