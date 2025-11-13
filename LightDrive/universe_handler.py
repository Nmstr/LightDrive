from data_structures import Universe
from PySide6.QtCore import QObject, Slot

class UniverseHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot(str)
    def add_universe(self, universe_name: str) -> None:
        if not universe_name:
            return
        self.root.workspace.universes.append(Universe(universe_name))
        self.root.data_models.build_universe_model()
