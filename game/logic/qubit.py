import collections
from abc import ABC, abstractmethod
from typing import List

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

    def to_string(self) -> str:
        text = ""
        for val in self.__amplitudes:
            val = np.round(val, StateVector.__DECIMALS)
            if val == 0:
                text += "0\n"
            else:
                text += f"{val}\n"
        return text

    def __str__(self) -> str:
        text = ""
        for val in self.__amplitudes:
            text += f"{np.round(val, StateVector.__DECIMALS)}\n"
        return text

    def __iter__(self) -> collections.Iterator:
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
        """

        :param amount: how much hp to heal
        :return: how much was actually healed (e.g. cannot exceed max health)
        """
        pass


class DummyQubitSet(QubitSet):
    __SIZE = 3
    __HP = 10

    def __init__(self, size: int = __SIZE):
        self.__hp = DummyQubitSet.__HP
        self.__size = size

    def hp(self) -> int:
        return self.__hp

    def is_alive(self) -> bool:
        return self.__hp > 0

    def size(self) -> int:
        return self.__size

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
