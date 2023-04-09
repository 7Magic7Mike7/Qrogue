import unittest
from typing import List

from qrogue.game.logic.actors import Robot
from qrogue.game.logic.collectibles import Instruction, GateType
from util_classes import LinkedList


class MyTestCase(unittest.TestCase):
    class GateDummy(Instruction):
        def __init__(self, needed_qubits: int, character: str):
            import qiskit.circuit.library.standard_gates as gates
            super().__init__(GateType.DummyGate, gates.IGate(), needed_qubits)

            self.qargs: List[int] = []
            self.needed_qubits: int = needed_qubits
            self.character = character[0]

        def abbreviation(self, qubit: int = 0):
            return self.character

        def copy(self) -> "Instruction":
            return MyTestCase.GateDummy(self.needed_qubits, self.character)

        def __str__(self):
            return f"{self.character} ({self.qargs})"

    # noinspection GrazieInspection
    def test_linked_list(self):
        content = [1, 2, 3, 4, 5, 6, 7]
        linked_list = LinkedList(content)

        # test len()
        self.assertEqual(len(linked_list), len(content), f"LinkedList has wrong len: "
                                                         f"{len(linked_list)} != {len(content)}")

        # test if get() doesn't alter the data structure
        val0 = linked_list.get(0)
        val1 = linked_list.get(0)
        self.assertEqual(val0, val1, f"linked_list.get(0) returned two different values: {val0} != {val1}")

        # test if get() returns expected value
        for i, val in enumerate(content):
            self.assertEqual(val, linked_list.get(i), f"Expected {val-1} but got {linked_list.get(val)}")

        # test if remove() works on heads
        for i, val in enumerate(content):
            # check if the new head is correct
            self.assertEqual(val, linked_list.get(0), f"Expected current head to be {val} but got {linked_list.get(0)}")
            # remove current head
            self.assertTrue(linked_list.remove(val), f"Failed to remove {val}. LinkedList = {linked_list}")
            # we should no longer be able to get() the previously last element since the length shrunk
            self.assertEqual(None, linked_list.get(len(content) - i), f"Expected None but got {linked_list.get(val)}")
        self.assertEqual(0, len(linked_list), f"Expected len=0 but got {len(linked_list)}")

        linked_list = LinkedList(content, capacity=2)
        self.assertNotEqual(len(linked_list), len(content), f"LinkedList has wrong len: "
                                                            f"{len(linked_list)} == {len(content)}")
        self.assertTrue(linked_list.is_full, "LinkedList should be full!")

        # test if only the expected elements are in our capped list
        for i in range(len(linked_list)):
            self.assertEqual(content[i], linked_list.get(i), f"Expected {content[i]} but got {linked_list.get(i)}")
        self.assertFalse(linked_list.insert(2, 0), "Successfully inserted value even though the list should be full!")

        # test insert()
        linked_list = LinkedList(capacity=5)
        self.assertTrue(linked_list.is_empty)
        self.assertFalse(linked_list.is_full)
        self.assertEqual(None, linked_list.get(0))

        for val in content:
            if linked_list.is_full:
                self.assertFalse(linked_list.insert(val, 0), "Inserting in a full list should fail!")
            else:
                self.assertTrue(linked_list.insert(val, 0), f"Failed to insert {val}!")

        self.assertTrue(linked_list.remove(3), "Failed to remove 3!")
        self.assertTrue(linked_list.insert(7, 3), "Failed to insert 7 at 3")
        self.assertEqual(7, linked_list.get(3), f"Expected 7 but got {linked_list.get(3)} at 3")
        print(linked_list)

    def test_circuit_grid(self):
        num_of_qubits = 2
        circuit_space = 5
        grid = Robot.CircuitGrid(num_of_qubits, circuit_space)

        placements = [
            (GateDummy(1, "A"), 0, 1),
            (GateDummy(1, "B"), 0, 1),
            (GateDummy(1, "C"), 0, 0),

            (GateDummy(1, "E"), 1, 0),

            (GateDummy(2, "G"), [0, 1], 2),
            (GateDummy(1, "D"), 1, 2),
        ]
        for data in placements:
            gate, qubit, pos = data
            grid.place(gate, qubit, pos)
            print(grid)

        order = [
            ["C", "A", "G", "B", ],
            ["E", None, "G", "D", ]
        ]
        for qubit in range(num_of_qubits):
            for pos in range(circuit_space):
                if pos < len(order[qubit]) and order[qubit][pos] is not None:
                    self.assertEqual(order[qubit][pos], grid.get(qubit, pos).character)
                else:
                    self.assertEqual(None, grid.get(qubit, pos))


if __name__ == '__main__':
    unittest.main()
