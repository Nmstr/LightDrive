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

    @Slot(str)
    def remove_universe(self, universe_uuid: str) -> None:
        if not universe_uuid:
            return
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                self.root.workspace.universes.remove(universe)
                break
        self.root.data_models.build_universe_model()

    @Slot(str, str)
    def configure_universe(self, universe_uuid: str, name: str) -> None:
        if not universe_uuid:
            return
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                universe_data = universe
                break
        else:
            return

        universe_data.name = name

    @Slot(str, result=list)  # Return is a list instead of a tuple because of qml types
    def get_universe_configuration(self, universe_uuid: str) -> list:
        if not universe_uuid:
            return []
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                return [universe.name]
        else:
            return []

    @Slot(str, bool, str, int, int)
    def configure_tcp_backend(self, universe_uuid: str, enabled: bool, target_ip: str, port: int, hz: int) -> None:
        if not universe_uuid:
            return
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                universe_data = universe
                break
        else:
            return

        universe_data.tcp_backend.enabled = enabled
        universe_data.tcp_backend.target_ip = target_ip
        universe_data.tcp_backend.port = port
        universe_data.tcp_backend.hz = hz

    @Slot(str, result=list)  # See reason for type above
    def get_tcp_backend_configuration(self, universe_uuid: str) -> list:
        if not universe_uuid:
            return []
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                return [universe.tcp_backend.enabled, universe.tcp_backend.target_ip, universe.tcp_backend.port, universe.tcp_backend.hz]
        else:
            return []