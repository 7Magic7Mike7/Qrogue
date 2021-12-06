from abc import ABC, abstractmethod

import numpy as np


class StateVector:
    __TOLERANCE = 0.1
    __DECIMALS = 3
    __SQRT05 = np.sqrt(0.5)

    def __init__(self, amplitudes: "list of complex numbers"):
        self.__amplitudes = amplitudes

    @property
    def size(self):
        return len(self.__amplitudes)

    @property
    def num_of_qubits(self) -> int:
        return int(np.log2(self.size))

    def to_value(self) -> "list of floats":
        return [np.round(val.real**2 + val.imag**2, decimals=StateVector.__DECIMALS) for val in self.__amplitudes]

    def is_equal_to(self, other, tolerance: float = __TOLERANCE) -> bool:
        if type(other) is not type(self):
            return False
        # other_value needs at least as many entries as self_value, more are allowed
        #  (so the player can have more qubits than the enemy)
        if self.size > other.size:
            return False
        self_value = self.__amplitudes #self.to_value()
        other_value = other.__amplitudes #other.to_value()
        for i in range(len(self_value)):
            p_min = self_value[i] - tolerance/2
            p = other_value[i]
            p_max = self_value[i] + tolerance/2
            if not (p_min <= p <= p_max):
                return False
        return True

    def get_diff(self, other: "StateVector") -> "StateVector":
        if self.size == other.size:
            diff = [self.__amplitudes[i] - other.__amplitudes[i] for i in range(self.size)]
            return StateVector(diff)
        else:
            return None

    def __eq__(self, other) -> bool: # TODO currently not even in use!
        if type(other) is type(self):
            return self.__amplitudes == other.__amplitudes
        elif type(other) is type([True, False]):  # TODO how to check correctly for bool-list?
            if len(other) >= len(self.__amplitudes):
                for i in range(len(self.__amplitudes)):
                    if self.__amplitudes[i] == 1 and not other[i] or self.__amplitudes[i] == 0 and other[i]:
                        return False
                return True
            return False
        elif type(other) is type([1.0, 0.0]):  # TODO how to check correctly for float-list?
            if len(other) >= len(self.__amplitudes):
                for i in range(len(self.__amplitudes)):
                    if self.__amplitudes[i] != other[i]:
                        return False
                return True
            return False
        return False

    def __str__(self) -> str:
        text = ""
        for val in self.__amplitudes:
            text += f"{np.round(val, 2)}\n"
        return text

    def __iter__(self) -> "iterator":
        return iter(self.__amplitudes)


# interface for a set of qubits (e.g. Ion-traps, Super conducting, ...)
class QubitSet(ABC):
    @abstractmethod
    def hp(self):
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def damage(self, amount: int) -> int:
        """

        :param amount: the amount of damage that should be received
        :return: the amount of damage actually received, negative if the damage was lethal
        """
        pass

    @abstractmethod
    def heal(self, amount: int) -> int:
        pass


class EmptyQubitSet(QubitSet):
    def hp(self):
        pass

    def is_alive(self) -> bool:
        return False

    def size(self) -> int:
        return 0

    def damage(self, amount: int) -> int:
        pass

    def heal(self, amount: int) -> int:
        pass


class DummyQubitSet(QubitSet):
    __SIZE = 2
    __HP = 10

    def __init__(self):
        self.__hp = DummyQubitSet.__HP

    def hp(self) -> int:
        return self.__hp

    def is_alive(self) -> bool:
        return self.__hp > 0

    def size(self) -> int:
        return self.__SIZE

    def damage(self, amount: int) -> int:
        self.__hp = max(self.__hp - amount, 0)
        if self.is_alive():
            return amount
        else:
            return -amount

    def heal(self, amount: int) -> int:
        if self.__hp + amount > DummyQubitSet.__HP:
            amount = DummyQubitSet.__HP - self.__hp
        self.__hp += amount
        return amount

