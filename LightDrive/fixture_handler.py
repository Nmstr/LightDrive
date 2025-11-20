from PySide6.QtCore import QObject, Slot

class FixtureHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot(str, str, int, str)
    def instantiate(self, name: str, universe_uuid: str, address: int, blueprint_path: str) -> None:
        print(name, universe_uuid, address, blueprint_path)
