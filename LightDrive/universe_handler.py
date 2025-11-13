from data_structures import Universe
from PySide6.QtCore import QObject, Slot

class UniverseHandler(QObject):
    def __init__(self, workspace):
        super().__init__()
        self.workspace = workspace

    @Slot()
    def add_universe(self):
        self.workspace.universes.append(Universe("Universe 1"))
