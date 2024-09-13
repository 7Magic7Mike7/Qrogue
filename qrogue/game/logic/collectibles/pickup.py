from abc import ABC
from typing import Optional, Callable

from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import Logger


class Pickup(Collectible, ABC):
    def __init__(self, amount: int, type_: CollectibleType = CollectibleType.Pickup):
        super(Pickup, self).__init__(type_)
        if amount <= 0:
            amount = 1
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def __str__(self):
        return self.to_string()


class Score(Pickup):
    def __init__(self, amount: int = 100):
        if amount < 0:
            Logger.instance().warn(f"Negative amount (={amount}) defined! Will use 0 instead.")
            amount = 0
        super().__init__(amount, type_=CollectibleType.Score)

    def name(self) -> str:
        return "Score"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Score describes how well you performed in a level."

    def to_string(self) -> str:
        return f"Score #{self.amount}"


class Key(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(amount, type_=CollectibleType.Key)

    def name(self) -> str:
        return "Key"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Keys are useful for opening locked doors."

    def to_string(self):
        if self.amount > 1:
            return f"{self.amount} keys"
        return f"{self.amount} key"


class Energy(Pickup):
    def __init__(self, amount: int = 10):
        super().__init__(amount, type_=CollectibleType.Energy)

    def name(self) -> str:
        return "Energy"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Gives back some energy to the Robot so it can stay longer on a mission."

    def to_string(self) -> str:
        return f"Energy ({self.amount})"


class Qubit(Collectible):
    __MIN_NUM = 1
    __MAX_NUM = 3

    def __init__(self, num: int = 1):
        if self.__MIN_NUM <= num <= self.__MAX_NUM:
            super().__init__(CollectibleType.Qubit)
            self.__num = num
        else:
            raise ValueError(f"Error trying to add to many qubits: {num}! Only between {self.__MIN_NUM} and "
                             f"{self.__MAX_NUM} allowed at once.")

    @property
    def additional_qubits(self) -> int:
        return self.__num

    def name(self) -> str:
        return "Qubit"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Qubits are the essence of any circuit you create."

    def to_string(self) -> str:
        return f"Qubit ({self.additional_qubits})"
