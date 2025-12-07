from data_structures import Fixture
from abc import ABC, abstractmethod

class GenericOutputSnippet(ABC):
    @abstractmethod
    def __init__(self, root):
        self._root = root

    @abstractmethod
    def get_values(self) -> dict[int, int]:  # { channel_number: value }
        pass

    def _get_fixture(self, fixture_uuid: str) -> Fixture | None:
        for fixture in self._root.workspace.fixtures:
            if fixture.uuid == fixture_uuid:
                return fixture
        return None
