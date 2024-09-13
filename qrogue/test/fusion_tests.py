import unittest

from qrogue.game.logic.collectibles.instruction import *
from qrogue.test.test_util import SingletonSetupTestCase
from qrogue.util import QuantumSimulationConfig, OptionsManager, Options


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

    def test_single_qubit_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 1
        gate1 = XGate().setup([0])
        gate2 = HGate().setup([0])

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, name="Test").setup([0])

        seq_matrix = self.__compute(num_of_qubits, [gate1, gate2], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_double_qubit_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 2
        gate1 = HGate().setup([0])
        gate2 = CXGate().setup([0, 1])

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, name="Test").setup([0, 1])

        seq_matrix = self.__compute(num_of_qubits, [gate1, gate2], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_reverse_order_fusion(self):
        unitary_simulator = UnitarySimulator()
        num_of_qubits = 2
        gate1 = CXGate().setup([0, 1], position=1)
        gate2 = HGate().setup([0], position=0)

        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, name="Test").setup([0, 1])

        seq_matrix = self.__compute(num_of_qubits, [gate2, gate1], unitary_simulator)
        comb_matrix = self.__compute(num_of_qubits, [comb_gate], unitary_simulator)

        self.assertEqual(seq_matrix, comb_matrix)

    def test_name(self):
        self.assertTrue(InstructionConfig.COMB_GATE_NAME_MIN_CHARACTERS > 0,
                        f"Minimum number of characters={InstructionConfig.COMB_GATE_MIN_GATE_NUM} is not > 0!")
        self.assertTrue(
            InstructionConfig.COMB_GATE_NAME_MAX_CHARACTERS >= InstructionConfig.COMB_GATE_NAME_MIN_CHARACTERS,
            f"Maximum number of gates={InstructionConfig.COMB_GATE_NAME_MAX_CHARACTERS} is smaller than "
            f"minimum number of gates={InstructionConfig.COMB_GATE_NAME_MIN_CHARACTERS}!")

        name = "Tes"
        exp_name = name + " Gate"

        comb_gate1 = CombinedGate([HGate().setup([0])], 1, name=name)              # no "Gate" suffix
        comb_gate2 = CombinedGate([HGate().setup([0])], 1, name=name + "Gate")     # "Gate" suffix without whitespace
        self.assertEqual(exp_name, comb_gate1.name())
        self.assertEqual(exp_name, comb_gate2.name())

        self.assertEqual(1, CombinedGate.validate_gate_name(""), "Failed to check for not enough characters")
        self.assertEqual(2, CombinedGate.validate_gate_name("TestGate"), "Failed to check for too many characters")
        self.assertEqual(3, CombinedGate.validate_gate_name("Te Gate"), "Failed to check for illegal characters")
        self.assertEqual(4, CombinedGate.validate_gate_name("X"), "Failed to check for equivalence to base gates")

    def test_instructions(self):
        self.assertTrue(InstructionConfig.COMB_GATE_MIN_GATE_NUM > 0,
                        f"Minimum number of gates={InstructionConfig.COMB_GATE_MIN_GATE_NUM} is not > 0!")
        self.assertTrue(InstructionConfig.COMB_GATE_MAX_GATE_NUM >= InstructionConfig.COMB_GATE_MIN_GATE_NUM,
                        f"Maximum number of gates={InstructionConfig.COMB_GATE_MAX_GATE_NUM} is smaller than "
                        f"minimum number of gates={InstructionConfig.COMB_GATE_MIN_GATE_NUM}!")

        # check min and max number of gates
        gate_list = [XGate()] * (InstructionConfig.COMB_GATE_MIN_GATE_NUM - 1)
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list)
        self.assertEqual(1, exit_code, "Failed to recognize that not enough gates were provided.")
        gate_list = [HGate()] * (InstructionConfig.COMB_GATE_MAX_GATE_NUM + 1)
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list)
        self.assertEqual(2, exit_code, "Failed to recognize that too many gates were provided.")

        # check number of QuantumFusers
        gate_list = [HGate()] * InstructionConfig.COMB_GATE_MAX_GATE_NUM
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list, InstructionConfig.COMB_GATE_MAX_GATE_NUM-1)
        self.assertEqual(3, exit_code, "Failed to recognize that not enough QuantumFusers are available.")

        gate_list = [HGate()]
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list, 0)
        self.assertEqual(3, exit_code, "Failed to recognize that not enough QuantumFusers are available.")

        # check fusing a CombinedGate
        gate_list = [CombinedGate([HGate().setup([0]), CXGate().setup([0, 1])], 2, name="Test")]
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list)
        self.assertEqual(4, exit_code, "Failed to recognize that a CombinedGate was fused.")

        # check for setup
        gate_list = [HGate()] * InstructionConfig.COMB_GATE_MIN_GATE_NUM
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list)
        self.assertEqual(5, exit_code, "Failed to recognize that an Instruction was not setup.")

        # check for success
        gate_list = [HGate().setup([0])] * InstructionConfig.COMB_GATE_MIN_GATE_NUM
        exit_code, exit_data = CombinedGate.validate_instructions(gate_list)
        self.assertEqual(0, exit_code, "Failed to recognize valid instructions.")

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
        self.assertTrue(OptionsManager.set_option_value(Options.show_ket_notation, True),
                        "Failed to activate ket-notation.")

        num_of_qubits = 2
        gate1 = HGate().setup([0])
        gate2 = CXGate().setup([0, 1])
        comb_gate = CombinedGate([gate1, gate2], num_of_qubits, name="Test").setup([0, 1])

        self.assertEqual(exp_desc, comb_gate.description(lambda unlock: True))


if __name__ == '__main__':
    unittest.main()
