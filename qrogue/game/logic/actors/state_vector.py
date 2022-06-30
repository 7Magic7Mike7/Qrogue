from collections import Iterator
from typing import List

import numpy as np
from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from qrogue.game.logic.collectibles import Instruction
from qrogue.util import Logger, QuantumSimulationConfig
from qrogue.util.config import ColorCode, ColorConfig
from qrogue.util.util_functions import is_power_of_2, center_string, to_binary_string, align_string


class StateVector:
    @staticmethod
    def check_amplitudes(amplitudes: List[complex]):
        if is_power_of_2(len(amplitudes)):
            amp_sum = sum([c.real**2 + c.imag**2 for c in amplitudes])
            return 1 - QuantumSimulationConfig.TOLERANCE <= amp_sum <= 1 + QuantumSimulationConfig.TOLERANCE
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
        val = np.round(val, QuantumSimulationConfig.DECIMALS)
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

    @staticmethod
    def complex_to_amplitude_percentage_string(val: complex) -> str:
        amp = np.round(abs(val**2), QuantumSimulationConfig.DECIMALS)
        text = str(amp * 100)
        if text[-2:] == ".0":
            text = text[:-2]    # remove the redundant ".0"
        return text + "%"

    @staticmethod
    def wrap_in_qubit_conf(state_vector: "StateVector", index: int,
                           space_per_value: int = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER, coloring: bool = False,
                           correct_amplitude: bool = False, show_percentage: bool = False):
        qubit_conf = f"|{to_binary_string(index, state_vector.num_of_qubits)}>"
        value = f"{center_string(StateVector.complex_to_string(state_vector.at(index)), space_per_value)}"
        if coloring:
            if correct_amplitude:
                value = ColorConfig.colorize(ColorCode.CORRECT_AMPLITUDE, value)
            else:
                value = ColorConfig.colorize(ColorCode.WRONG_AMPLITUDE, value)
        if show_percentage:
            value += f"  ({StateVector.complex_to_amplitude_percentage_string(state_vector.at(index))})"
        return f"{qubit_conf}  {value}"

    @staticmethod
    def create_zero_state_vector(num_of_qubits: int) -> "StateVector":
        amplitudes = [1] + [0] * (2**num_of_qubits - 1)
        return StateVector(amplitudes)

    def __init__(self, amplitudes: List[complex]):
        self.__amplitudes = amplitudes

    @property
    def size(self) -> int:
        return len(self.__amplitudes)

    @property
    def num_of_qubits(self) -> int:
        return int(np.log2(self.size))

    @property
    def is_zero(self) -> bool:
        for val in self.__amplitudes:
            if abs(val) > QuantumSimulationConfig.TOLERANCE:
                return False
        return True

    def at(self, index: int) -> complex:
        if 0 <= index < self.size:
            return self.__amplitudes[index]

    def to_value(self) -> List[float]:
        return [np.round(val.real ** 2 + val.imag ** 2, decimals=QuantumSimulationConfig.DECIMALS) for val in self.__amplitudes]

    def is_equal_to(self, other, tolerance: float = QuantumSimulationConfig.TOLERANCE) -> bool:
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
            if abs(val) > tolerance:
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

    def to_string(self, space_per_value: int = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER) -> str:
        text = ""
        for i in range(self.size):
            text += StateVector.wrap_in_qubit_conf(self, i, space_per_value)
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
            text += f"{np.round(val, QuantumSimulationConfig.DECIMALS)}, "
        text = text[:-2] + ")"
        return text

    def __iter__(self) -> Iterator:
        return iter(self.__amplitudes)


class CircuitMatrix:
    def __init__(self, matrix: List[List[complex]]):
        self.__matrix = matrix

    @property
    def size(self) -> int:
        return len(self.__matrix)

    @property
    def num_of_qubits(self) -> int:
        return int(np.log2(self.size))

    def to_string(self, space_per_value: int = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER) -> str:
        text = " " * (1 + self.num_of_qubits + 1)   # we need to pad the rows' |qubits> prefix
        for i in range(self.size):
            text += center_string(f"|{to_binary_string(i, self.num_of_qubits)}>", space_per_value)
        text += "\n"
        for i, row in enumerate(self.__matrix):
            text += f"|{to_binary_string(i, self.num_of_qubits)}> "
            for val in row:
                text += center_string(StateVector.complex_to_string(val), space_per_value)
                text += " "
            text += "\n"
        return text

    def __str__(self) -> str:
        text = "CircuitMatrix("
        for row in self.__matrix:
            for val in row:
                text += f"{np.round(val, QuantumSimulationConfig.DECIMALS)}, "
            text += "\n"
        text = text[:-2] + ")"
        return text
