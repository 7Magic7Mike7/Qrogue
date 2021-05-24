from abc import ABC

from game.collectibles.collectible import Collectible, CollectibleType


class Pickup(Collectible, ABC):
    def __init__(self, type: CollectibleType, amount: int):
        super(Pickup, self).__init__(type)
        self._amount = amount

    @property
    def amount(self):
        return self._amount


class Coin(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(CollectibleType.Coin, amount)

    def name(self) -> str:
        return "Coin"

    def description(self) -> str:
        return "Coins are used to buy Collectibles from the Shop"

    def __str__(self):
        return f"{self.amount}$"


class Key(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(CollectibleType.Key, amount)

    def name(self) -> str:
        return "Key"

    def description(self) -> str:
        return "A Key is useful for opening locked doors."

    def __str__(self):
        return f"{self.amount} key(s)"


class Heart(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(CollectibleType.Heart, amount)

    def name(self) -> str:
        return "Heart"

    def description(self) -> str:
        return "A Heart gives you back some of your HP."

    def __str__(self) -> str:
        return f"Heart ({self.amount} HP)"
