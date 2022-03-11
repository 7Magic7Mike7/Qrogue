
from abc import ABC, abstractmethod
from typing import Tuple


# interface for a set of qubits (e.g. Ion-traps, Super conducting, ...)
class QubitSet(ABC):
    def __init__(self, max_hp: int, size: int):
        self._max_hp = max_hp
        self._cur_hp = max_hp
        self._size = size

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def hp(self) -> int:
        return self._cur_hp

    @property
    def size(self) -> int:
        return self._size

    def is_alive(self) -> bool:
        return self.hp > 0

    @abstractmethod
    def damage(self, amount: int) -> Tuple[int, bool]:
        """

        :param amount: the amount of damage that should be received
        :return: the amount of damage actually received, whether the damage was deadly or not
        """
        pass

    @abstractmethod
    def heal(self, amount: int) -> int:
        """

        :param amount: how much hp to heal
        :return: how much was actually healed (e.g. cannot exceed max health)
        """
        pass

    @abstractmethod
    def add_qubits(self, additional_qubits: int = 1) -> "QubitSet":
        pass


class DummyQubitSet(QubitSet):
    __SIZE = 2
    __HP = 10

    def __init__(self, size: int = __SIZE):
        super(DummyQubitSet, self).__init__(DummyQubitSet.__HP, size)

    def damage(self, amount: int) -> Tuple[int, bool]:
        self._cur_hp = max(self.hp - amount, 0)
        return amount, not self.is_alive()

    def heal(self, amount: int) -> int:
        if self.hp + amount > self.max_hp:
            amount = self.max_hp - self.hp
        self._cur_hp += amount
        return amount

    def add_qubits(self, additional_qubits: int = 1) -> "QubitSet":
        return DummyQubitSet(self.size + additional_qubits)
