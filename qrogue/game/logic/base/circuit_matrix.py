from typing import List, Optional, Union

import numpy as np

from qrogue.util import Logger, QuantumSimulationConfig, GameplayConfig, Options, Config
from qrogue.util.quantum_functions import generate_ket, verify_circuit_matrix
from qrogue.util.util_functions import center_string, complex2string
from .state_vector import StateVector


class CircuitMatrix:
    @staticmethod
    def create_identity(num_of_qubits: int) -> "CircuitMatrix":
        matrix = []
        for i in range(2 ** num_of_qubits):
            row = [0] * 2 ** num_of_qubits
            row[i] = 1
            matrix.append(row)
        return CircuitMatrix(matrix, num_of_used_gates=0)

    @staticmethod
    def check_validity(matrix: List[List[complex]]) -> bool:
        col_sum: List[float] = [0] * len(matrix)
        for row in matrix:
            row_sum = 0
            for i, val in enumerate(row):
                res_val = abs(val) ** 2
                row_sum += res_val
                col_sum[i] += res_val
            if row_sum < 1 - QuantumSimulationConfig.TOLERANCE or 1 + QuantumSimulationConfig.TOLERANCE < row_sum:
                return False
        for val in col_sum:
            if val < 1 - QuantumSimulationConfig.TOLERANCE or 1 + QuantumSimulationConfig.TOLERANCE < val:
                return False
        return True

    @staticmethod
    def matrix_to_string(matrix: Union[List[List[complex]], np.ndarray], num_of_qubits: int,
                         space_per_value: Optional[int] = None) -> str:
        if isinstance(matrix, np.ndarray):
            assert len(matrix.shape) == 2 and matrix.shape[0] == matrix.shape[1], \
                f"matrix needs to be 2D and quadratic, but is: {matrix.shape}"
        if space_per_value is None:
            # use the maximum space by default, so we definitely have enough space
            space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_COMPLEX_NUMBER

        spacing = " "
        if GameplayConfig.get_option_value(Options.show_ket_notation, convert=True):
            padding = len(generate_ket(0, num_of_qubits)) + len(spacing)  # also add the space after the ket
            text = " " * padding  # we need to pad the rows' |qubits> prefix
            for i in range(2 ** num_of_qubits):
                # space_per_value + 1 due to the trailing space
                text += center_string(generate_ket(i, num_of_qubits), space_per_value)
                text += spacing
            text += "\n"
        else:
            text = "\n"
        for i, row in enumerate(matrix):
            if GameplayConfig.get_option_value(Options.show_ket_notation, convert=True):
                text += generate_ket(i, num_of_qubits)
                text += spacing
            for val in row:
                decimals = QuantumSimulationConfig.COMPLEX_DECIMALS if val.real != 0 and val.imag != 0 \
                    else QuantumSimulationConfig.DECIMALS
                text += center_string(complex2string(val, decimals), space_per_value)
                text += spacing
            text += "\n"
        return text

    def __init__(self, matrix: List[List[complex]], num_of_used_gates: int):
        self.__matrix = matrix
        self.__num_of_used_gates = num_of_used_gates

        if not verify_circuit_matrix(matrix, QuantumSimulationConfig.TOLERANCE):
            debug = True

    @property
    def size(self) -> int:
        return len(self.__matrix)

    @property
    def num_of_qubits(self) -> int:
        return int(np.log2(self.size))

    @property
    def num_of_used_gates(self) -> int:
        return self.__num_of_used_gates

    @property
    def is_classical(self) -> bool:
        mat_sum = 0
        for row in self.__matrix:
            for val in row:
                if val != 0 and val != 1:
                    return False
                mat_sum += val
        return mat_sum == self.size  # there needs to be one 1 per row

    @property
    def is_real(self) -> bool:
        for row in self.__matrix:
            for val in row:
                if val.imag != 0:
                    return False
        return True

    @property
    def is_imag(self) -> bool:
        for row in self.__matrix:
            for val in row:
                if val.real != 0:
                    return False
        return True

    @property
    def is_complex(self) -> bool:
        # if it's neither pure real nor pure imaginary it has to be mixed and therefore complex
        return not self.is_real and not self.is_imag

    def multiply(self, stv: StateVector) -> Optional[StateVector]:  # todo improve performance?
        if self.num_of_qubits == stv.num_of_qubits:
            values = []
            for row in self.__matrix:
                val = 0
                for i, entry in enumerate(row):
                    val += entry * stv.at(i)
                values.append(val)
            return StateVector(values, self.num_of_used_gates +
                               (0 if stv.num_of_used_gates is None else stv.num_of_used_gates))
        else:
            Logger.instance().error(f"@multiply: CircuitMatrix (={self.num_of_qubits}) and Stv (={stv.num_of_qubits}) "
                                    f"don't have the same number of qubits!", show=Config.debugging(), from_pycui=False)
            return None

    def to_string(self, space_per_value: Optional[int] = None) -> str:
        if space_per_value is None:
            if self.is_complex:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_COMPLEX_NUMBER
            elif self.is_imag:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER + 1
            else:
                space_per_value = QuantumSimulationConfig.MAX_SPACE_PER_NUMBER

        return CircuitMatrix.matrix_to_string(self.__matrix, self.num_of_qubits, space_per_value)

    def __eq__(self, other):
        if not isinstance(other, CircuitMatrix): return False
        if other.size != self.size: return False

        for y in range(self.size):
            for x in range(self.size):
                if other.__matrix[y][x] != self.__matrix[y][x]:
                    return False
        return True

    def __str__(self) -> str:
        text = "CircuitMatrix("
        for row in self.__matrix:
            for val in row:
                text += f"{np.round(val, QuantumSimulationConfig.DECIMALS)}, "
            text += "\n"
        text = text[:-2] + ")"
        return text
