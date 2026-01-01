from output.output_backends.generic_output_backend import GenericOutputBackend
from pyartnet import ArtNetNode
import threading
import asyncio

class ArtNetBackend(GenericOutputBackend):
    def __init__(self, target_ip: str, universe: int, max_fps: int, refresh_every: int) -> None:
        super().__init__()
        self._target_ip = target_ip
        self._universe = universe
        self._max_fps = max_fps
        self._refresh_every = refresh_every
        self._values = [0] * 512
        self._running = False
        self._config_changed = False
        self._worker_task = None

        self._start_worker()

    def set_values(self, values: list[int]) -> None:
        self._values = values

    def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def _run_worker(self):
        self._running = True
        while self._running:
            async with ArtNetNode.create(self._target_ip, max_fps=self._max_fps, refresh_every=self._refresh_every) as node:
                universe = node.add_universe(self._universe)
                channel = universe.add_channel(start=1, width=512)

                while not self._config_changed:
                    channel.set_values(values=self._values)
                    await asyncio.sleep(1 / self._max_fps)  # There is no reason to refresh quicker than the max fps
                self._config_changed = False

    def _start_worker(self) -> None:
        loop = asyncio.new_event_loop()
        self._worker_task = loop.create_task(self._run_worker())
        worker_thread = threading.Thread(target=self._run_loop, args=(loop,))
        worker_thread.start()

    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def update_configuration(self, target_ip: str, universe: int, max_fps: int, refresh_every: int) -> None:
        self._target_ip = target_ip
        self._universe = universe
        self._max_fps = max_fps
        self._refresh_every = refresh_every
        self._config_changed = True
