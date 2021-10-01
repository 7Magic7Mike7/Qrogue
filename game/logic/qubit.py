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

    def to_value(self):
        return [np.round(val.real**2 + val.imag**2, decimals=StateVector.__DECIMALS) for val in self.__amplitudes]

    def is_equal_to(self, other, tolerance: float = __TOLERANCE):
        if type(other) is not type(self):
            return False
        # other_value needs at least as many entries as self_value, more are allowed
        #  (so the player can have more qubits than the enemy)
        if self.size > other.size:
            return False
        self_value = self.to_value()
        other_value = other.to_value()
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

    def __eq__(self, other):
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

    def __str__(self):
        text = ""
        for val in self.__amplitudes:
            text += f"{np.round(val, 2)}\n"
        return text


# interface for a set of qubits (e.g. Ion-traps, Super conducting, ...)
class QubitSet:
    def is_alive(self):
        pass

    def size(self):
        pass

    def damage(self, dmg_0: int, dmg_1):
        pass


class EmptyQubitSet(QubitSet):
    def is_alive(self):
        return False

    def size(self):
        return 0

    def damage(self, dmg_0: int, dmg_1):
        pass


class DummyQubitSet(QubitSet):
    __SIZE = 3
    __HP_0 = 5
    __HP_1 = 4

    def __init__(self):
        self.__hp_0 = self.__HP_0
        self.__hp_1 = self.__HP_1

    def is_alive(self):
        return self.__hp_0 > 0 and self.__hp_1 > 0

    def size(self):
        return self.__SIZE

    def damage(self, dmg_0: int, dmg_1):
        self.__hp_0 = max(self.__hp_0 - dmg_0, 0)
        self.__hp_1 = max(self.__hp_1 - dmg_1, 0)
