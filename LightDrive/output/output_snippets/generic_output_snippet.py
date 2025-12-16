from data_structures import Fixture
from abc import ABC, abstractmethod

class GenericOutputSnippet(ABC):
    @abstractmethod
    def __init__(self, root, priority: int):
        self._root = root
        self._priority = priority

    @abstractmethod
    def get_values(self) -> dict[str, dict[int, int]]:  # { universe_uuid: { channel_number: value } }
        pass

    def _get_fixture(self, fixture_uuid: str) -> Fixture | None:
        for fixture in self._root.workspace.fixtures:
            if fixture.uuid == fixture_uuid:
                return fixture
        return None

    @property
    def priority(self) -> int:
        return self._priority

    def __eq__(self, other: "GenericOutputSnippet") -> bool:
        if not isinstance(other, GenericOutputSnippet):
            return False
        return self.priority == other.priority

    def __ne__(self, other: "GenericOutputSnippet") -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: "GenericOutputSnippet") -> bool:
        if not isinstance(other, GenericOutputSnippet):
            return False
        return self.priority < other.priority

    def __le__(self, other: "GenericOutputSnippet") -> bool:
        if not isinstance(other, GenericOutputSnippet):
            return False
        return self.priority <= other.priority

    def __gt__(self, other: "GenericOutputSnippet") -> bool:
        if not isinstance(other, GenericOutputSnippet):
            return False
        return self.priority > other.priority

    def __ge__(self, other: "GenericOutputSnippet") -> bool:
        if not isinstance(other, GenericOutputSnippet):
            return False
        return self.priority >= other.priority
