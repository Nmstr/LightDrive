from abc import ABC, abstractmethod

class GenericOutputBackend(ABC):
    @abstractmethod
    def set_values(self, values: list[int]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
