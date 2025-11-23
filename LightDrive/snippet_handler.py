from snippet_subhandlers import scene_subhandler
from PySide6.QtCore import QObject, Slot

class SnippetHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.scene_subhandler = scene_subhandler.SceneSubhandler(self.root)

    @Slot(result=QObject)
    def get_scene_subhandler(self) -> scene_subhandler.SceneSubhandler:
        return self.scene_subhandler
