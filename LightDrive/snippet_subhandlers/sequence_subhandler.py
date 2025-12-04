from data_structures import SequenceSnippet
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QObject, Slot, Qt, QByteArray

class SequenceSubhandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

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
    def add_scene(self, snippet_uuid: str, scene_uuid: str) -> None:
        print(snippet_uuid, scene_uuid)
