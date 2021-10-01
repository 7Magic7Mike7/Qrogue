import numpy as np

from util.my_random import RandomManager


class Qubit:    # TODO introduce interface, for example for only zero_life and one_life qubits
    def __init__(self, index: int, zero_life: int, one_life: int):
        self.index = index
        self.__zero_life = zero_life
        self.__one_life = one_life
        self.__cur_zlife = zero_life
        self.__cur_olife = one_life

    def __str__(self):
        return f"q_{self.index} ({self.__cur_zlife}|{self.__cur_olife})"

    def damage(self, value: int, dmg: int = 1):
        if value == 0:
            self.__cur_zlife -= dmg
        else:
            self.__cur_olife -= dmg

    def get_zero_life(self):
        return self.__zero_life

    def get_one_life(self):
        return self.__one_life

    def get_cur_life(self):
        return self.__cur_zlife, self.__cur_olife

    def is_alive(self):
        return self.__cur_zlife > 0 and self.__cur_olife > 0


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

    def to_value(self, size: int = 0):
        #raise NotImplementedError("Continue here!")
        """
        rand = RandomManager.instance().get()
        probability = 0.0
        for i in range(len(self.val)):
            state_probability = self.val[i]**2
            if probability <= rand < probability + state_probability:
                return i
            probability += state_probability
        return len(self.val)-1
        """
        value = [np.round(val.real**2 + val.imag**2, decimals=StateVector.__DECIMALS) for val in self.__amplitudes]
        if size <= 0:
            return value
        elif size <= self.size:
            # todo
            # e.g. [0 0 0.71 0.71] to [0 1] or [0.5 0.5 0.5 0.5] to [0.71 0.71] or [0.71 0 0 0.71] to [0.71 0.71]
            raise NotImplementedError("Continue here!")
        else:
            raise ValueError(f"Unable to extend StateVector of size = {self.size} to {size}")

    def extend(self, add_qubits: int):  # TODO remove? target-initialization at fight start might be a better idea
        if add_qubits < 0:
            raise ValueError(f"$add_qubits must not be negative: {add_qubits}")
        amps = [0 for i in range(self.size)]
        if RandomManager.instance().get() < 0.5:
            self.__amplitudes = amps + self.__amplitudes
        else:
            self.__amplitudes = self.__amplitudes + amps
        """
        for i in range(add_qubits):
            amps = []
            for a in self.__amplitudes: # TODO loops can be optimized
                val = a * self.__SQRT05
                amps.append(val)
                amps.append(val)
            self.__amplitudes = amps
            print("amps: ", self.__amplitudes)
        """
        """
        [a b] -> [sqrt(a/2) sqrt(a/2) sqrt(b/2) sqrt(b/2)}
        """

    def is_equal_to(self, other, tolerance: float = __TOLERANCE):
        if type(other) is not type(self):
            return False
        # other_value needs at least as many entries as self_value, more are allowed
        #  (so the player can have more qubits than the enemy)
        if self.size > other.size:
            return False
        self_value = self.to_value()
        other_value = other.to_value()
        print("-----")
        for i in range(len(self_value)):
            p_min = self_value[i] - tolerance/2
            p = other_value[i]
            p_max = self_value[i] + tolerance/2
            print(f"{i}: {p_min:.2} <= {p:.2} <= {p_max:.2}")
            if not (p_min <= p <= p_max):
                return False
        print("-----")
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
