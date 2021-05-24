from abc import ABC, abstractmethod
from enum import Enum


class CollectibleType(Enum):
    Consumable = 1
    Gate = 2
    ActiveItem = 3
    PassiveItem = 4
    Coin = 5
    Key = 6
    Heart = 7


def type_str(type: CollectibleType) -> str:
    if type is CollectibleType.Gate:
        return " Gate"
    else:
        return ""


class Collectible(ABC):
    def __init__(self, type: CollectibleType):
        self.__type = type

    @property
    def type(self):
        return self.__type

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def __str__(self):
        pass


class ShopItem:
    def __init__(self, collectible: Collectible, price: int):
        self.__collectible = collectible
        self.__price = price

    @property
    def collectible(self) -> Collectible:
        return self.__collectible

    @property
    def price(self) -> int:
        return self.__price

    def __str__(self):
        return f"{self.collectible}, {self.price}$"
