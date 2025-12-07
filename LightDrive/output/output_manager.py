from data_structures import Universe
from output_snippets.generic_output_snippet import GenericOutputSnippet
from output_universe import OutputUniverse

class OutputManager:
    def __init__(self, root):
        self.root = root
        self.universes: list[OutputUniverse] = []

    def build_output_universes(self, universes: list[Universe]) -> None:
        """
        Create the output universes as required.
        """
        pass

    def add_snippet(self, universe_uuid: str, priority: int, snippet: GenericOutputSnippet) -> None:
        pass

    def remove_snippet(self, universe_uuid: str, snippet: GenericOutputSnippet) -> None:
        pass
