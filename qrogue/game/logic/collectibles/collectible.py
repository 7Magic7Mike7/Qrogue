from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterator, List, Callable, Optional


class CollectibleType(Enum):
    # Consumable = 1      # currently unused
    ActiveItem = 3      # currently unused
    PassiveItem = 4     # currently unused

    Multi = 0   # wraps multiple collectibles
    Gate = 2
    Qubit = 6

    Pickup = 5  # for undefined pickups
    Key = 51
    # Coin = 52
    Energy = 53
    Score = 54


class Collectible(ABC):
    def __init__(self, c_type: CollectibleType):
        self.__type = c_type

    @property
    def type(self):
        return self.__type

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass


class MultiCollectible(Collectible):
    PRICE_MULT = 0.9

    def __init__(self, content: List[Collectible]):
        super(MultiCollectible, self).__init__(CollectibleType.Multi)
        self.__content = content

    def name(self) -> str:
        return "Collectible Pack"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        desc = "Contains multiple Collectibles:"
        for collectible in self.__content:
            desc += "\n  - " + collectible.name()
        return desc

    def to_string(self) -> str:
        text = "Multi ["
        for collectible in self.__content:
            text += collectible.to_string() + ", "
        return text + "]"

    def iterator(self) -> Iterator[Collectible]:
        return iter(self.__content)
