from output.output_snippets.generic_output_snippet import GenericOutputSnippet
from output.output_universe import OutputUniverse

class OutputManager:
    def __init__(self, root):
        self.root = root
        self.universes: list[OutputUniverse] = []

    def build_output_universes(self) -> None:
        """
        Create the output universes as required.
        """
        for universe in self.root.workspace.universes:  # Add all universes
            if universe.uuid in [universe.uuid for universe in self.universes]:
                continue  # Universe already exists (here we don't force rebuild to preserve running snippets)

            # Add the universe
            output_universe = OutputUniverse(universe)
            self.universes.append(output_universe)

        # Remove universes that don't exist anymore
        for universe in self.universes:
            if universe.uuid not in [universe.uuid for universe in self.root.workspace.universes]:
                self.universes.remove(universe)

    def add_snippet(self, universe_uuid: str, priority: int, snippet: GenericOutputSnippet) -> None:
        pass

    def remove_snippet(self, universe_uuid: str, snippet: GenericOutputSnippet) -> None:
        pass
