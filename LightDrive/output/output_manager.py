from output.output_snippets.generic_output_snippet import GenericOutputSnippet
from output.output_universe import OutputUniverse
from PySide6.QtCore import QTimer
import queue

class OutputManager:
    def __init__(self, root):
        self.root = root
        self.snippet_queue = queue.PriorityQueue()
        self.pending_removal_snippets: list[GenericOutputSnippet] = []
        self.universes: list[OutputUniverse] = []

        self.update_timer = QTimer()
        self.update_timer.setInterval(10)
        self.update_timer.timeout.connect(lambda: self.update_universes())
        self.update_timer.start()

    def build_output_universes(self) -> None:
        """
        Create the output universes as required.
        """
        for universe in self.universes:  # Update all backends of all existing universes
            universe.update_backends()

        for universe in self.root.workspace.universes:  # Add all universes
            if universe.uuid in [universe.uuid for universe in self.universes]:
                continue  # Universe already exists

            # Add the universe
            output_universe = OutputUniverse(universe)
            output_universe.build_backends()
            self.universes.append(output_universe)

        # Remove universes that don't exist anymore
        for universe in self.universes:
            if universe.uuid not in [universe.uuid for universe in self.root.workspace.universes]:
                self.universes.remove(universe)

    def add_snippet(self, snippet: GenericOutputSnippet) -> None:
        self.snippet_queue.put(snippet)

    def remove_snippet(self, snippet: GenericOutputSnippet) -> None:
        self.pending_removal_snippets.append(snippet)

    def update_universes(self) -> None:
        """
        Updates all the universes with up-to-date values
        """
        done_queue = queue.PriorityQueue()
        values: dict[str, list[int]] = {}
        for universe in self.universes:
            values[universe.uuid] = [0] * 512

        # Build the output list
        while not self.snippet_queue.empty():
            snippet = self.snippet_queue.get()

            if snippet in self.pending_removal_snippets:  # Remove snippet
                self.pending_removal_snippets.remove(snippet)
                continue

            done_queue.put(snippet)
            for universe_uuid, universe_values in snippet.get_values().items():
                for channel, value in universe_values.items():
                    values[universe_uuid][channel] = value
        self.snippet_queue = done_queue

        # Send output list to output backends
        for universe in self.universes:
            if universe.uuid in values:
                universe.tick_output(values[universe.uuid])
