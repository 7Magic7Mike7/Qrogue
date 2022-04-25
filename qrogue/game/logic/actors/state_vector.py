from collections import Iterator
from typing import List

import numpy as np
from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from qrogue.game.logic.collectibles import Instruction
from qrogue.util import Logger
from qrogue.util.util_functions import is_power_of_2


class StateVector:
    __TOLERANCE = 0.1
    __DECIMALS = 3

    @staticmethod
    def check_amplitudes(amplitudes: List[complex]):
        if is_power_of_2(len(amplitudes)):
            amp_sum = sum([c.real**2 + c.imag**2 for c in amplitudes])
            return 1 - StateVector.__TOLERANCE <= amp_sum <= 1 + StateVector.__TOLERANCE
        return False

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
            text = f"{val.real:g}"  # g turns 0.0 to 0
        elif val.real == 0:
            text = f"{val.imag:g}j"
        else:
            if val.imag == 1:
                text = f"{val.real:g}+j"
            elif val.imag == -1:
                text = f"{val.real:g}-j"
            else:
                text = str(val)[1:-1]    # remove the parentheses
        # skip "-" in front if the text starts with "-0" and the value is actually 0 (so no more comma)
        if text.startswith("-0") and (len(text) == 2 or len(text) > 2 and text[2] != "."):
            text = text[1:]
        return text

    def __init__(self, amplitudes: List[complex]):
        self.__amplitudes = amplitudes

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
        """
        self_value = self.__amplitudes  #self.to_value()
        other_value = other.__amplitudes    #other.to_value()
        for i in range(len(self_value)):
            p_min = self_value[i] - tolerance/2         # todo maybe tolerance doesn't work for imaginary numbers?
            p = other_value[i]
            p_max = self_value[i] + tolerance/2
            if not (p_min <= p <= p_max):
                return False
        """
        diff = [self.__amplitudes[i] - other.__amplitudes[i] for i in range(self.size)]
        for val in diff:
            if abs(val) < -self.__TOLERANCE or self.__TOLERANCE < abs(val):
                return False
        return True

    def get_diff(self, other: "StateVector") -> "StateVector":
        if self.size == other.size:
            diff = [self.__amplitudes[i] - other.__amplitudes[i] for i in range(self.size)]
            return StateVector(diff)
        elif self.size < other.size:
            Logger.instance().info("Requested difference between StateVectors of different sizes! "
                                   f"self = {self}, other = {other}; padding self with the needed number of 0s",
                                   from_pycui=False)
            diff = [0] * other.size
            for i in range(self.size):
                diff[i] = self.__amplitudes[i] - other.__amplitudes[i]
            return StateVector(diff)
        else:
            raise ValueError("Cannot calculate the difference between StateVectors of different size! "
                             f"self = {self}, other = {other}")

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

    def __iter__(self) -> Iterator:
        return iter(self.__amplitudes)

