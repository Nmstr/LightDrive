from data_structures import Universe, UniverseTcpBackend
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

    @Slot(str, bool, str, int)
    def configure_tcp_backend(self, universe_uuid: str, enabled: bool, target_ip: str, port: int) -> None:
        if not universe_uuid:
            return
        for universe in self.root.workspace.universes:
            if universe.uuid == universe_uuid:
                universe_data = universe
                break
        else:
            return

        # Create the backend if it does not exist
        if UniverseTcpBackend() not in universe_data.backends:
            universe_data.backends.append(UniverseTcpBackend())

        # Configure the backend
        for backend in universe_data.backends:
            if backend == UniverseTcpBackend():
                backend.enabled = enabled
                backend.target_ip = target_ip
                backend.port = port
                break
