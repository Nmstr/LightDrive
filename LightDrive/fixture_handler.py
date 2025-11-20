from data_structures import Fixture, Channel
from PySide6.QtCore import QObject, Slot
import pathlib
import json

class FixtureHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot(str, str, int, str)
    def instantiate(self, name: str, universe_uuid: str, address: int, blueprint_path: str) -> None:
        if not name or not universe_uuid or not address or not blueprint_path:
            return

        path = pathlib.Path(blueprint_path)
        with open(path, "r") as file:
            blue_data = json.load(file)
        channels = []
        for channel in blue_data["channels"]:
            channels.append(Channel(channel.get("type", "unknown"), channel.get("name", "Unknown")))

        fixture = Fixture(name=name, universe_uuid=universe_uuid, address=address,
                          type=blue_data.get("type", "unknown"), manufacturer=blue_data.get("manufacturer", "Unknown"), channels=channels)
        self.root.workspace.fixtures.append(fixture)
        self.root.data_models.build_fixtures_model()
