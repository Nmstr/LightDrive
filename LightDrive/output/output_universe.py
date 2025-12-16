from data_structures import Universe
from output.output_backends.generic_output_backend import GenericOutputBackend
from output.output_backends.tcp_backend import TcpBackend

class OutputUniverse:
    def __init__(self, universe_data: Universe):
        self._universe_data = universe_data
        self.output_backends: list[GenericOutputBackend] = []

    def build_backends(self):
        self.output_backends = []
        if self._universe_data.tcp_backend.enabled:
            target_ip = self._universe_data.tcp_backend.target_ip
            port = self._universe_data.tcp_backend.port
            hz = self._universe_data.tcp_backend.hz
            tcp_backend = TcpBackend(target_ip, port, hz)
            self.output_backends.append(tcp_backend)

    def tick_output(self, values: list[int]) -> None:
        """
        Sends data from the snippets to all output backends.
        """
        for backend in self.output_backends:
            backend.set_values(values)

    @property
    def uuid(self) -> str:
        return self._universe_data.uuid
