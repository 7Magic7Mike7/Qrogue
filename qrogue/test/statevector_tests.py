import unittest

import numpy as np

import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.logic.actors.puzzles import is_puzzle_solvable
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Instruction
from qrogue.test import test_util


class StateVectorTests(test_util.SingletonSetupTestCase):
    _SUP_VAL = 1 / np.sqrt(2)

    def test_gate_order(self):
        # both puzzles should be solvable, because they only differ in the order gates appear in gate_list
        input_stv = StateVector([0, 0, 0, 0,
                                 complex(0, -1), 0, 0, 0])
        target_stv = Instruction.compute_stv([gates.HGate().setup([1])], 3)

        gate_list1 = [gates.XGate(), gates.CXGate(), gates.HGate(), gates.SGate()]
        ret1, _ = is_puzzle_solvable(input_stv, target_stv, gate_list1)
        self.assertTrue(ret1, "Failed to solve solvable puzzle!")

        gate_list2 = [gates.HGate(), gates.SGate(), gates.XGate(), gates.CXGate()]
        ret2, _ = is_puzzle_solvable(input_stv, target_stv, gate_list2)
        self.assertTrue(ret2, "Failed to solve solvable puzzle!")

    def test2(self):
        # todo: this one claims to not be reachable, but it is { H @q1, X @g1 }
        input_stv = StateVector([0, 0, 1, 0,
                                 0, 0, 0, 0])
        target_stv = StateVector([-StateVectorTests._SUP_VAL, 0, StateVectorTests._SUP_VAL, 0,
                                  0, 0, 0, 0])
        ret, circuit = is_puzzle_solvable(input_stv, target_stv, [gates.HGate(), gates.XGate(), gates.CXGate()])
        print("Is reachable? ", ret)
        print(circuit)
        self.assertTrue(ret)

        gate_list = [gates.XGate().setup([1]), gates.HGate().setup([0]), gates.SGate().setup([1]),
                     gates.CXGate().setup([1, 0])]
        target_stv = Instruction.compute_stv(gate_list, num_of_qubits=2)
        print(target_stv.to_string())


if __name__ == '__main__':
    unittest.main()