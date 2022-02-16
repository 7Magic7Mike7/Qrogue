import collections
from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np
from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from game.logic.instruction import Instruction


class StateVector:
    __TOLERANCE = 0.1
    __DECIMALS = 3

    def __init__(self, amplitudes: List[complex]):
        self.__amplitudes = amplitudes

    @staticmethod
    def from_gates(gates: List[Instruction], num_of_qubits: int) -> "StateVector":
        circuit = QuantumCircuit(num_of_qubits, num_of_qubits)
        for instruction in gates:
            instruction.append_to(circuit)
        simulator = StatevectorSimulator()
        compiled_circuit = transpile(circuit, simulator)
        # We only do 1 shot since we don't need any measurement but the StateVector
        job = simulator.run(compiled_circuit, shots=1)
        return StateVector(job.result().get_statevector())

    @staticmethod
    def complex_to_string(val: complex) -> str:
        val = np.round(val, StateVector.__DECIMALS)
        if val.imag == 0:
            return f"{val.real:g}"
        elif val.real == 0:
            return f"{val.imag:g}j"
        else:
            if val.imag == 1:
                return f"{val.real:g}+j"
            elif val.imag == -1:
                return f"{val.real:g}-j"
            else:
                return str(val)[1:-1]    # remove the parentheses

    @property
    def size(self) -> int:
        return len(self.__amplitudes)

    @property
    def num_of_qubits(self) -> int:
        return int(np.log2(self.size))

    def to_value(self) -> List[float]:
        return [np.round(val.real**2 + val.imag**2, decimals=StateVector.__DECIMALS) for val in self.__amplitudes]

    def is_equal_to(self, other, tolerance: float = __TOLERANCE) -> bool:
        if type(other) is not type(self):
            return False
        # other_value needs at least as many entries as self_value, more are allowed
        #  (so the robot can have more qubits than the enemy)
        if self.size > other.size:
            return False
        self_value = self.__amplitudes  #self.to_value()
        other_value = other.__amplitudes    #other.to_value()
        for i in range(len(self_value)):
            p_min = self_value[i] - tolerance/2         # todo maybe tolerance doesn't work for imaginary numbers?
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

    def to_string(self) -> str:
        text = ""
        for val in self.__amplitudes:
            text += StateVector.complex_to_string(val)
            text += "\n"
        return text

    def __eq__(self, other) -> bool: # TODO currently not even in use!
        if type(other) is type(self):
            return self.__amplitudes == other.__amplitudes
        elif isinstance(other, list):
            if len(other) <= 0 or len(other) >= len(self.__amplitudes):
                return False
            if isinstance(other[0], bool):
                for i in range(len(self.__amplitudes)):
                    if self.__amplitudes[i] == 1 and not other[i] or self.__amplitudes[i] == 0 and other[i]:
                        return False
                return True
            elif isinstance(other[0], float):
                for i in range(len(self.__amplitudes)):
                    if self.__amplitudes[i] != other[i]:
                        return False
                return True
        return False

    def __str__(self) -> str:
        text = "StateVector("
        for val in self.__amplitudes:
            text += f"{np.round(val, StateVector.__DECIMALS)}, "
        text = text[:-2] + ")"
        return text

    def __iter__(self) -> collections.Iterator:
        return iter(self.__amplitudes)


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
