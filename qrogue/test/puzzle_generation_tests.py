import unittest
from typing import List, Dict, Set

import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.logic import PuzzleGenerator
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Score
from qrogue.test import test_util
from qrogue.util import RandomManager, StvDifficulty
from qrogue.util.stv_difficulty import DifficultyType


class ManuelPuzzleGenTestCase(test_util.SingletonSetupTestCase):
    def test_something(self):
        rm = RandomManager.create_new(7)
        num_of_qubits = 3
        circuit_space = 5
        available_gates = [gates.HGate(), gates.XGate(), gates.SGate(), gates.XGate(), gates.HGate()]
        available_gates = [gates.XGate(), gates.XGate(), gates.XGate()]

        difficulty = StvDifficulty.from_difficulty_level(2)
        difficulty = test_util.ExplicitStvDifficulty({
            DifficultyType.CircuitExuberance: len(available_gates) + 1
        }, num_of_qubits, circuit_space)

        input_stv, target_stv, reward = PuzzleGenerator.generate_puzzle(rm, num_of_qubits, circuit_space, difficulty,
                                                                    available_gates, include_gates=[gates.CXGate()],
                                                                    reward_pool=[Score()])

    def test_stv1(self):
        num_of_qubits = 2
        gate_list = [gates.XGate().setup([0]), gates.XGate().setup([1]), gates.XGate().setup([0])]

        stv_storage: List[StateVector] = [StateVector.create_zero_state_vector(num_of_qubits)]
        circuits: List[List[gates.Instruction]] = [[]]
        for cur_gate in gate_list:
            new_circuits: List[List[gates.Instruction]] = []
            for circuit in circuits:
                new_circuit = circuit.copy() + [cur_gate]
                new_stv = gates.Instruction.compute_stv(new_circuit, num_of_qubits)

                is_repeat = False
                for prev_stv in stv_storage:
                    if prev_stv.is_equal_to(new_stv, ignore_god_mode=True):
                        is_repeat = True
                        break
                if not is_repeat:
                    stv_storage.append(new_stv)
                    new_circuits.append(new_circuit)
            circuits += new_circuits

        equality_dict: Dict[StateVector, List[List[gates.Instruction]]] = {}
        for circuit in circuits:
            stv = gates.Instruction.compute_stv(circuit, num_of_qubits)
            if stv not in equality_dict:
                equality_dict[stv] = []
            equality_dict[stv].append(circuit)

        for stv, circuit_list in equality_dict.items():
            print(stv)
            for circ in circuit_list:
                print(f"\t{', '.join([str(g) for g in circ])}")
            print()

    def test_stv2(self):
        num_of_qubits = 2
        gate_list = [gates.XGate().setup([0]), gates.XGate().setup([1]), gates.XGate().setup([0])]

        stv_storage: Set[StateVector] = {StateVector.create_zero_state_vector(num_of_qubits)}
        circuits: List[List[gates.Instruction]] = [[]]
        for cur_gate in gate_list:
            real_circuit = circuits[-1]
            new_stv = gates.Instruction.compute_stv(real_circuit.copy() + [cur_gate], num_of_qubits)

            is_repeat = False
            for prev_stv in stv_storage:
                if prev_stv.is_equal_to(new_stv, ignore_god_mode=True):
                    is_repeat = True
                    break

            if not is_repeat:
                #stv_storage.add(new_stv)   # not needed since the same Stv is already added in below loop
                # append cur_gate to all possible previous gates
                new_circuits = []
                for circuit in circuits:
                    new_circuit = circuit.copy() + [cur_gate]
                    new_circuits.append(new_circuit)
                    stv_storage.add(gates.Instruction.compute_stv(new_circuit, num_of_qubits))
                circuits += new_circuits

        equality_dict: Dict[StateVector, List[List[gates.Instruction]]] = {}
        for circuit in circuits:
            stv = gates.Instruction.compute_stv(circuit, num_of_qubits)
            if stv not in equality_dict:
                equality_dict[stv] = []
            equality_dict[stv].append(circuit)

        for stv, circuit_list in equality_dict.items():
            print(stv)
            for circ in circuit_list:
                print(f"\t{', '.join([str(g) for g in circ])}")
            print()

        print("Real circuit:")
        print(f"\t{', '.join([str(g) for g in circuits[-1]])}")
        print(gates.Instruction.compute_stv(circuits[-1], num_of_qubits))
        print()


if __name__ == '__main__':
    unittest.main()
