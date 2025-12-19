from output.output_snippets.sequence_output_snippet import SequenceOutputSnippet
from data_structures import SequenceSnippet, SequenceSceneEntry, SceneSnippet
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QObject, Slot, Qt, QByteArray

class SequenceSubhandler(QObject):
    def __init__(self, root, snippet_handler):
        super().__init__(snippet_handler)
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

        for scene_entry in snippet.scenes:
            scene = self.snippet_handler.get_snippet(scene_entry.scene_uuid)
            scene_item = QStandardItem(scene.name)
            scene_item.setData(scene_entry.scene_uuid, Qt.UserRole)
            scene_item.setData(scene_entry.fade_in, Qt.UserRole + 1)
            scene_item.setData(scene_entry.duration, Qt.UserRole + 2)
            scene_item.setData(scene_entry.fade_out, Qt.UserRole + 3)
            sequence_model.appendRow(scene_item)

        self.root.snippet_handler.loadSequence.emit(snippet.uuid, snippet.name, sequence_model)

    @Slot(str)
    def output_sequence(self, sequence_uuid: str) -> None:
        sequence = self.root.snippet_handler.get_snippet(sequence_uuid)
        if not sequence:
            return

        output_snippet = SequenceOutputSnippet(self.root, 0, sequence)
        self.root.snippet_handler.output_snippets[sequence_uuid] = output_snippet
        self.root.output_manager.add_snippet(output_snippet)

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

        # Reload
        self.load(snippet)
