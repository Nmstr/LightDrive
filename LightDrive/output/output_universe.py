from data_structures import Universe, UniverseTcpBackend
from output.output_snippets.generic_output_snippet import GenericOutputSnippet
from output.output_backends.generic_output_backend import GenericOutputBackend
from output.output_backends.tcp_backend import TcpBackend
import queue

class OutputUniverse:
    def __init__(self, universe_data: Universe):
        self._universe_data = universe_data
        self.snippet_queue = queue.PriorityQueue()
        self.pending_removal_snippets: list[GenericOutputSnippet] = []
        self.output_backends: list[GenericOutputBackend] = []

    def build_backends(self):
        self.output_backends = []
        for backend in self._universe_data.backends:
            match backend:
                case UniverseTcpBackend():
                    backend = TcpBackend()
            self.output_backends.append(backend)

    def add_snippet(self, snippet: GenericOutputSnippet) -> None:
        self.snippet_queue.put(snippet)

    def remove_snippet(self, snippet: GenericOutputSnippet) -> None:
        self.pending_removal_snippets.append(snippet)

    def tick_output(self) -> None:
        """
        Sends data from the snippets to all output backends.
        """
        done_queue = queue.PriorityQueue()
        values = [0] * 256

        # Build the output list
        while not self.snippet_queue.empty():
            snippet = self.snippet_queue.get()

            if snippet in self.pending_removal_snippets:  # Remove snippet
                self.pending_removal_snippets.remove(snippet)
                continue

            done_queue.put(snippet)
            for channel, value in snippet.get_values().items():
                values[channel] = value
        self.snippet_queue = done_queue

        # Send output list to output backends
        for backend in self.output_backends:
            backend.set_values(values)

    @property
    def uuid(self) -> str:
        return self._universe_data.uuid
