from PySide6.QtCore import QObject, Slot

class SceneSubhandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot()
    def add(self):
        print("add scene")
