import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterator


class CollectibleType(Enum):
    Consumable = 1
    Gate = 2
    ActiveItem = 3
    PassiveItem = 4
    Pickup = 5
    Qubit = 6

    Multi = 0   # wraps multiple collectibles


def type_str(c_type: CollectibleType) -> str:
    if c_type is CollectibleType.Gate:
        return " Gate"
    else:
        return ""


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
    def description(self) -> str:
        pass

    @abstractmethod
    def default_price(self) -> int:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass


class MultiCollectible(Collectible):
    PRICE_MULT = 0.9

    def __init__(self, content: [Collectible]):
        super(MultiCollectible, self).__init__(CollectibleType.Multi)
        self.__content = content

    def name(self) -> str:
        return "Collectible Pack"

    def description(self) -> str:
        desc = "Contains multiple Collectibles:"
        for collectible in self.__content:
            desc += "\n  - " + collectible.name()
        return desc

    def default_price(self) -> int:
        price = 0
        for collectible in self.__content:
            price += collectible.default_price()
        return math.ceil(price * MultiCollectible.PRICE_MULT)

    def to_string(self) -> str:
        text = "Multi ["
        for collectible in self.__content:
            text += collectible.to_string() + ", "
        return text + "]"

    def iterator(self) -> Iterator[Collectible]:
        return iter(self.__content)


class ShopItem:
    def __init__(self, collectible: Collectible, price: int = -1):
        self.__collectible = collectible
        if price < 0:
            price = collectible.default_price()
        self.__price = price

    @property
    def collectible(self) -> Collectible:
        return self.__collectible

    @property
    def price(self) -> int:
        return self.__price

    def to_string(self) -> str:
        return f"{self.collectible}, {self.price}$"

    def __str__(self):
        return self.to_string()
