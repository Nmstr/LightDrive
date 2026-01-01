from output.output_backends.generic_output_backend import GenericOutputBackend
from stupidArtnet import StupidArtnet

class ArtNetBackend(GenericOutputBackend):
    def __init__(self, target_ip: str, universe: int, fps: int) -> None:
        super().__init__()
        self._target_ip = target_ip
        self._universe = universe
        self._fps = fps

        self._packet_size = 512
        self._device = self.create_device()

    def create_device(self) -> StupidArtnet:
        device = StupidArtnet(target_ip=self._target_ip, universe=self._universe, packet_size=self._packet_size, fps=self._fps, broadcast=True)
        device.start()
        return device

    def set_values(self, values: list[int]) -> None:
        self._device.set(values)

    def stop(self) -> None:
        self._device.blackout()
        self._device.stop()

    def update_configuration(self, target_ip: str, universe: int, fps: int) -> None:
        self._target_ip = target_ip
        self._universe = universe
        self._fps = fps

        self.stop()
        self._device = self.create_device()
