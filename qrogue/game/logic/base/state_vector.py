from typing import Iterator, List, Optional

import numpy as np

from qrogue.util import Logger, QuantumSimulationConfig, GameplayConfig, Options, CheatConfig
from qrogue.util.config import ColorCode, ColorConfig
from qrogue.util.quantum_functions import generate_ket, verify_stv_amplitudes
from qrogue.util.util_functions import center_string, align_string, complex2string


def _wrap_in_ket_notation(number: complex, qubit: int, num_of_qubits: int,
                          decimals: Optional[int] = None, space_per_value: Optional[int] = None, coloring: bool = False,
                          correct_amplitude: bool = False, show_percentage: bool = False, skip_ket: bool = False):
    """

    :param number:
    :param qubit:
    :param num_of_qubits:
    :param decimals:
    :param space_per_value:
    :param coloring:
    :param correct_amplitude:
    :param show_percentage:
    :param skip_ket:
    :return:
    """
    is_complex = number.real != 0 and number.imag != 0
    if decimals is None:
        if is_complex:
            decimals = QuantumSimulationConfig.COMPLEX_DECIMALS
        else:
            decimals = QuantumSimulationConfig.DECIMALS

    if space_per_value is None:
        if is_complex:
            space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_COMPLEX_NUMBER
        elif number.imag != 0:
            space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER + 1  # add the extra "j"
        else:
            space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER

    value = f"{center_string(complex2string(number, decimals), space_per_value)}"
    if coloring:
        if correct_amplitude:
            value = ColorConfig.colorize(ColorCode.PUZZLE_CORRECT_AMPLITUDE, value)
        else:
            value = ColorConfig.colorize(ColorCode.PUZZLE_WRONG_AMPLITUDE, value)

    if show_percentage:
        space = QuantumSimulationConfig.MAX_PERCENTAGE_SPACE
        percentage = StateVector.complex_to_amplitude_percentage_string(number, space)
        space += 1  # +1 because of the additional "%" we have to align
        if percentage == "0%":
            value += f"  {align_string('', space, left=False)}"  # show whitespace instead of redundant 0% amplitudes
        else:
            value += f" ~{align_string(percentage, space, left=False)}"

    if GameplayConfig.get_option_value(Options.show_ket_notation, convert=True) and not skip_ket:
        return f"{generate_ket(qubit, num_of_qubits)}  {value}"
    else:
        return value


class StateVector:
    @staticmethod
    def check_amplitudes(amplitudes: List[complex]):
        return verify_stv_amplitudes(amplitudes, QuantumSimulationConfig.TOLERANCE)

    @staticmethod
    def complex_to_amplitude_percentage_string(val: complex,
                                               space: int = QuantumSimulationConfig.MAX_PERCENTAGE_SPACE) -> str:
        amp = np.round(abs(val ** 2), QuantumSimulationConfig.DECIMALS)
        text = str(amp * 100)
        if text[-2:] == ".0":
            text = text[:-2]  # remove the redundant ".0"
        if len(text) > space:
            text = text[:space]  # clamp to specified space
        return text + "%"

    @staticmethod
    def create_zero_state_vector(num_of_qubits: int) -> "StateVector":
        amplitudes = [1] + [0] * (2 ** num_of_qubits - 1)
        return StateVector(amplitudes, num_of_used_gates=0)

    @staticmethod
    def create_basis_states(num_of_qubits: int) -> List["StateVector"]:
        states = []
        for i in range(2 ** num_of_qubits):
            amplitudes = [0] * 2 ** num_of_qubits
            amplitudes[i] = 1
            states.append(StateVector(amplitudes, num_of_used_gates=0))
        return states

    def __init__(self, amplitudes: List[complex], num_of_used_gates: Optional[int] = None):
        self.__amplitudes = amplitudes
        self.__num_of_used_gates = num_of_used_gates

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

    @property
    def is_classical(self) -> bool:
        for val in self.__amplitudes:
            # if there is an imaginary part or the real part is anything except 0 or 1, the StateVector is not classical
            if val.imag != 0 or val.real not in [0, 1]:
                return False
        # if the sum is 1, we have exactly one 1 and everything else is 0 -> we have a classical state
        return sum(self.__amplitudes) == 1

    @property
    def is_real(self) -> bool:
        for val in self.__amplitudes:
            if val.imag != 0:
                return False
        return True

    @property
    def is_imag(self) -> bool:
        for val in self.__amplitudes:
            if val.real != 0:
                return False
        return True

    @property
    def is_complex(self) -> bool:
        # if it's neither pure real nor pure imaginary it has to be mixed and therefore complex
        return not self.is_real and not self.is_imag

    @property
    def num_of_used_gates(self) -> int:
        return self.__num_of_used_gates

    def at(self, index: int) -> complex:
        if 0 <= index < self.size:
            return self.__amplitudes[index]

    def to_value(self) -> List[float]:
        """
        Returns a list of amplitudes corresponding to this StateVector.

        :return: List of amplitudes
        """
        return [np.round(val.real ** 2 + val.imag ** 2, decimals=QuantumSimulationConfig.DECIMALS)
                for val in self.__amplitudes]

    def is_equal_to(self, other: "StateVector", tolerance: float = QuantumSimulationConfig.TOLERANCE,
                    ignore_god_mode: bool = False) -> bool:
        """

        :param other:
        :param tolerance:
        :param ignore_god_mode: whether we also want to check for equality when in god mode
        :return:
        """
        if not ignore_god_mode and CheatConfig.in_god_mode():
            return True

        # other needs at least as many entries as self_value, more are allowed
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
        """
        Calculates the difference of this and other, i.e. this - other, with basically normal vector subtraction rules.
        To be more specific, the difference of every amplitude entry of this and other is calculated and then used to
        create a new StateVector.
        In the special case of this being smaller in size than other, this is first extended with 0s before the
        difference is calculated the usual way.

        :param other: the StateVector we want to know the difference of
        :return: a new StateVector corresponding to this - other
        """
        assert self.size <= other.size, "Cannot calculate the difference between StateVectors of different size! " \
                                        f"self = {self}, other = {other}"

        if self.size == other.size:
            diff = [self.__amplitudes[i] - other.__amplitudes[i] for i in range(self.size)]
            return StateVector(diff)

        elif self.size < other.size:
            Logger.instance().info("Requested difference between StateVectors of different sizes! "
                                   f"self = {self}, other = {other}; padding self with the needed number of 0s",
                                   from_pycui=False)
            diff: List[complex] = [0] * other.size
            for i in range(self.size):
                diff[i] = self.__amplitudes[i] - other.__amplitudes[i]
            return StateVector(diff)

    def wrap_in_qubit_conf(self, index: int, space_per_value: Optional[int] = None, coloring: bool = False,
                           correct_amplitude: bool = False, show_percentage: bool = False, skip_ket: bool = False) \
            -> str:
        # don't use default decimals since we don't want it to be dependent on individual entries but rather decide
        # based on whether the vector itself is complex or not
        decimals = QuantumSimulationConfig.COMPLEX_DECIMALS if self.is_complex else QuantumSimulationConfig.DECIMALS
        if space_per_value is None:
            if self.is_complex:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_COMPLEX_NUMBER
            elif self.is_imag:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER + 1  # add the "j"
            else:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER

        return _wrap_in_ket_notation(self.at(index), index, self.num_of_qubits, decimals, space_per_value, coloring,
                                     correct_amplitude, show_percentage, skip_ket)

    def to_string(self, space_per_value: Optional[int] = None) -> str:
        text = ""
        for i in range(self.size):
            text += self.wrap_in_qubit_conf(i, space_per_value)
            text += "\n"
        return text

    def __eq__(self, other) -> bool:  # TODO currently not even in use!
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
