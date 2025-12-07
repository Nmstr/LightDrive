from data_structures import Universe
from output_snippets.generic_output_snippet import GenericOutputSnippet
from output_backends.generic_output_backend import GenericOutputBackend
import queue

class OutputUniverse:
    def __init__(self, root, universe_data: Universe):
        self.root = root
        self.universe_data = universe_data
        self.snippet_queue = queue.PriorityQueue()
        self.pending_removal_snippets: list[GenericOutputSnippet] = []
        self.output_backends: list[GenericOutputBackend] = []

    def add_snippet(self, priority: int, snippet: GenericOutputSnippet) -> None:
        self.snippet_queue.put((priority, snippet))

    def remove_snippet(self, snippet: GenericOutputSnippet) -> None:
        self.pending_removal_snippets.append(snippet)

    def tick_output(self) -> None:
        """
        Sends data from the snippets to all output backends.
        """
        pass

    @property
    def uuid(self) -> str:
        return self.universe_data.uuid
