import enum
from abc import ABC, abstractmethod
from typing import List

from qrogue.game.collectibles.collectible import Collectible


class ControllableType(enum.Enum):
    Player = "M"
    Luke = "L"
    Test = "T"

    @staticmethod
    def values() -> "List[ControllableType]":
        return [ControllableType.Player, ControllableType.Luke, ControllableType.Test]

    def __init__(self, abbreviation: str):
        self.__abbreviation = abbreviation

    @property
    def name(self) -> str:
        return self.__abbreviation


class Controllable(ABC):
    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @abstractmethod
    def key_count(self) -> int:
        pass

    @abstractmethod
    def use_key(self) -> bool:
        pass

    @abstractmethod
    def get_img(self):
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def give_collectible(self, collectible: Collectible):
        pass
