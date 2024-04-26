# exporting
from .target import Target
from .enemy import Enemy
from .boss import Boss
from .riddle import Riddle
from .challenge import Challenge

import itertools
from typing import Tuple, Optional, List
from qrogue.util import QuantumSimulationConfig
from ...base import CircuitMatrix, StateVector, QuantumCircuit, UnitarySimulator
from ...collectibles import Instruction


def is_puzzle_solvable(input_stv: StateVector, target_stv: StateVector, gate_list: List[Instruction]) \
        -> Tuple[bool, Optional[QuantumCircuit]]:
    assert input_stv.num_of_qubits == target_stv.num_of_qubits, "Different number of qubits!"

    simulator = UnitarySimulator()
    circuit = QuantumCircuit.from_bit_num(input_stv.num_of_qubits, input_stv.num_of_qubits)
    return __is_reachable_rec(simulator, circuit, input_stv, target_stv, gate_list)


def __is_reachable_rec(simulator: UnitarySimulator, circuit: QuantumCircuit, input_stv: StateVector,
                       target_stv: StateVector, gate_list: List["Instruction"]) \
        -> Tuple[bool, Optional[QuantumCircuit]]:
    cur_gate = gate_list.pop()
    qubits = list(itertools.permutations(range(input_stv.num_of_qubits), cur_gate.num_of_qubits))

    while len(qubits) > 0:
        cur_circuit = circuit.copy()
        qargs = qubits.pop()
        gate = cur_gate.copy().setup(qargs)
        gate.append_to(cur_circuit)

        amplitudes = simulator.execute(cur_circuit, decimals=QuantumSimulationConfig.DECIMALS)
        circuit_matrix = CircuitMatrix(amplitudes, 0)  # num of used gates doesn't matter when checking reachability
        cur_stv = circuit_matrix.multiply(input_stv)
        diff = cur_stv.get_diff(target_stv)

        if diff.is_zero:
            return True, cur_circuit

        # go one recursion step deeper and try the next gate
        if len(gate_list) > 0:
            ret, winning_circuit = __is_reachable_rec(simulator, cur_circuit, input_stv, target_stv,
                                                                  gate_list.copy())
            if ret: return True, winning_circuit
        # else we try to place cur_gate on different qubits and continue

    return False, None

# importing
# +util
# +collectibles
# +StateVector
