import unittest

from qrogue.game.logic.collectibles.instruction import *
from qrogue.test.test_util import SingletonSetupTestCase
from qrogue.util import QuantumSimulationConfig


class FusionTestCase(SingletonSetupTestCase):
    @staticmethod
    def __compute(num_of_qubits: int, instructions: List[Instruction], unitary_simulator: UnitarySimulator):
        num_of_used_gates: int = 0
        circuit = QuantumCircuit.from_bit_num(num_of_qubits, num_of_qubits)
        for inst in instructions:
            if inst is not None:
                num_of_used_gates += 1
                inst.append_to(circuit)

        amplitudes = unitary_simulator.execute(circuit, decimals=QuantumSimulationConfig.DECIMALS)
        return CircuitMatrix(amplitudes, num_of_used_gates)

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_single_qubit_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 1
        gate1 = XGate().setup([0])
        gate2 = HGate().setup([0])

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, label="Test").setup([0])

        seq_matrix = self.__compute(num_of_qubits, [gate1, gate2], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_double_qubit_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 2
        gate1 = HGate().setup([0])
        gate2 = CXGate().setup([0, 1])

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, label="Test").setup([0, 1])

        seq_matrix = self.__compute(num_of_qubits, [gate1, gate2], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_reverse_order_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 2
        gate1 = CXGate().setup([0, 1], position=1)
        gate2 = HGate().setup([0], position=0)

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, label="Test").setup([0, 1])

        seq_matrix = self.__compute(num_of_qubits, [gate2, gate1], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_name(self):
        name = "Test"
        exp_name = name + " Gate"

        comb_gate1 = CombinedGate([HGate().setup([0])], 1, label=name)              # no "Gate" suffix
        comb_gate2 = CombinedGate([HGate().setup([0])], 1, label=exp_name)          # "Gate" suffix with whitespace
        comb_gate3 = CombinedGate([HGate().setup([0])], 1, label=name + "Gate")     # "Gate" suffix without whitespace

        self.assertEqual(exp_name, comb_gate1.name())
        self.assertEqual(exp_name, comb_gate2.name())
        self.assertEqual(exp_name, comb_gate3.name())

    def test_description(self):
        exp_desc = """Abbreviation: Q0
This gate is a combination of multiple gates fused into one.

Matrix:
      |00>   |01>   |10>   |11>  
|00>  0.707  0.707    0      0   
|01>    0      0    0.707 -0.707 
|10>    0      0    0.707  0.707 
|11>  0.707 -0.707    0      0   

Underlying Circuit:
In | q1 >---------+--{ X }--< q'1 | Out
   | q0 >--{ H }--+--{ C }--< q'0 |    """

        num_of_qubits = 2
        gate1 = HGate().setup([0])
        gate2 = CXGate().setup([0, 1])
        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, label="Test").setup([0, 1])

        self.assertEqual(exp_desc, comb_gate.description(lambda unlock: True))


if __name__ == '__main__':
    unittest.main()
