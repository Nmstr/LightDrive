from abc import ABC, abstractmethod

class GenericOutputSnippet(ABC):
    @abstractmethod
    def get_values(self):
        pass
