from abc import ABC, abstractmethod

class GenericOutputBackend(ABC):
    @abstractmethod
    def set_values(self, values) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
