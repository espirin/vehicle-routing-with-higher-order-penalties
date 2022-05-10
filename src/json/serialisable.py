from abc import ABC, abstractmethod


class Serialisable(ABC):
    @abstractmethod
    def to_json(self):
        pass
