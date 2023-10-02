from typing import Optional, List

from qrogue.util.util_functions import to_binary_string, center_string, align_string, is_power_of_2


def generate_ket(qubit: int, num_of_qubits: int) -> str:
    """
    Generates a str for the ket notation of the given qubit. num_of_qubits is also needed to determine the number of
    leading 0s needed.
    Examples:
        - _generate_ket(1, 2) == "|01>"
        - _generate_ket(0, 1) == "|0>"
        - _generate_ket(3, 4) == "|0011>"

    :param qubit: the id (in terms of MSB-LSB) of the given qubit
    :param num_of_qubits: the number of qubits in the StateVector
    :return: ket notation of the given qubit as str
    """
    return f"|{to_binary_string(qubit, num_of_qubits)}>"


def verify_stv_amplitudes(amplitudes: List[complex], tolerance: float):
    if is_power_of_2(len(amplitudes)):
        amp_sum = sum([c.real**2 + c.imag**2 for c in amplitudes])
        return 1 - tolerance <= amp_sum <= 1 + tolerance
    return False


def verify_circuit_matrix(matrix: List[List[complex]], tolerance: float) -> bool:
    col_sum: List[float] = [0] * len(matrix)
    for row in matrix:
        row_sum = 0
        for i, val in enumerate(row):
            res_val = abs(val)**2
            row_sum += res_val
            col_sum[i] += res_val
        if row_sum < 1 - tolerance or 1 + tolerance < row_sum:
            return False
    for val in col_sum:
        if val < 1 - tolerance or 1 + tolerance < val:
            return False
    return True
