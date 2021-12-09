from abc import ABC, abstractmethod
from enum import Enum


class CollectibleType(Enum):
    Consumable = 1
    Gate = 2
    ActiveItem = 3
    PassiveItem = 4
    Pickup = 5


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
    def default_price(self) -> int:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass


class ShopItem:
    __BASE_UNIT = 1

    @staticmethod
    def base_unit() -> int:
        return ShopItem.__BASE_UNIT

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
