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

    def update_backends(self):
        def _get_backend(backend_type) -> GenericOutputBackend | None:
            for backend in self.output_backends:
                if type(backend) is backend_type:
                    return backend
            else:
                return None

        tcp_backend = _get_backend(TcpBackend)
        if tcp_backend and self._universe_data.tcp_backend.enabled:
            tcp_backend_data = self._universe_data.tcp_backend
            tcp_backend.update_configuration(tcp_backend_data.target_ip, tcp_backend_data.port, tcp_backend_data.hz)
        elif tcp_backend and not self._universe_data.tcp_backend.enabled:
            tcp_backend.stop()
            self.output_backends.remove(tcp_backend)
        elif not tcp_backend and self._universe_data.tcp_backend.enabled:
            tcp_backend_data = self._universe_data.tcp_backend
            tcp_backend = TcpBackend(tcp_backend_data.target_ip, tcp_backend_data.port, tcp_backend_data.hz)
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
