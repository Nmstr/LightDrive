from data_structures import Universe
from PySide6.QtCore import QObject, Slot

class UniverseHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot()
    def add_universe(self):
        self.root.workspace.universes.append(Universe("Universe 1"))
