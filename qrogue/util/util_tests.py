import unittest
from typing import List, Tuple, Union

from qrogue.game.logic.actors import Robot
from qrogue.game.logic.collectibles import Instruction, GateType
from qrogue.game.logic.collectibles.instruction import RelationalGridInstruction
from util_classes import LinkedList, RelationalGrid


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

    @staticmethod
    def __place_in_grid(grid: RelationalGrid, gates: List[GateDummy],
                        positioning: List[Tuple[Union[int, List[int]], int]]):
        for i, data in enumerate(positioning):
            gate = gates[i]
            qargs, pos = data
            if isinstance(qargs, int): qargs = [qargs]
            for qu in qargs: gate.use_qubit(qu)
            grid.place(RelationalGridInstruction(gate), pos)
            print(grid)

    def __check_order(self, grid: RelationalGrid, expected_order: List[List[GateDummy]]):
        for row in range(grid.num_of_rows):
            for col in range(grid.num_of_columns):
                if row >= len(expected_order) or col >= len(expected_order[row]): expected_item = None
                else: expected_item = expected_order[row][col]

                item = grid.get(row, col)
                if item is not None: item = item.value

                self.assertEqual(expected_item, item)

    def test_circuit_grid(self):
        grid = RelationalGrid.empty(2, 5)

        gates = [
            MyTestCase.GateDummy(1, "A"),
            MyTestCase.GateDummy(1, "B"),
            MyTestCase.GateDummy(1, "C"),
            MyTestCase.GateDummy(1, "E"),
            MyTestCase.GateDummy(2, "G"),
            MyTestCase.GateDummy(1, "D"),
        ]
        positioning = [
            (0, 1),
            (0, 1),
            (0, 0),

            (1, 0),

            ([0, 1], 2),
            (1, 2),
        ]
        self.__place_in_grid(grid, gates, positioning)

        A, B, C, E, G, D = gates[0], gates[1], gates[2], gates[3], gates[4], gates[5]
        order = [
            [C, A, G, B, ],
            [E, D, G, None, ]
        ]
        self.__check_order(grid, order)

        print("Iterating")
        gates_copy = gates.copy()
        text = ""
        for gate in grid:
            gates_copy.remove(gate)
            text += gate.character + ", "
        print(text[:-2])
        self.assertEqual(len(gates_copy), 0, f"Didn't iterate over all gates! {gates_copy} is missing")

    def test_circuit_grid2(self):
        # create a chain reaction of shifting multiple multi row items
        grid = RelationalGrid.empty(3, 4)
        gates = [
            MyTestCase.GateDummy(2, "C"),
            MyTestCase.GateDummy(2, "S"),
            MyTestCase.GateDummy(1, "X"),
            MyTestCase.GateDummy(1, "H"),
        ]
        positioning = [
            ([0, 1], 0),
            ([1, 2], 1),
            (0, 0),
            (0, 0),
        ]
        self.__place_in_grid(grid, gates, positioning)

        C, S, X, H = gates[0], gates[1], gates[2], gates[3]
        order = [
            [H, X, C, None],
            [None, None, C, S],
            [None, None, None, S],
        ]
        self.__check_order(grid, order)

    def test_circuit_grid3(self):
        # shift multi row item regardless of row order (e.g., the second row is shifted explicitly while the first row
        # only shift implicitly)
        grid = RelationalGrid.empty(3, 3)
        gates = [
            MyTestCase.GateDummy(2, "C"),
            MyTestCase.GateDummy(1, "X"),
            MyTestCase.GateDummy(1, "H"),
        ]
        positioning = [
            ([0, 1], 0),
            (1, 0),
            (1, 0),
        ]
        self.__place_in_grid(grid, gates, positioning)

        C, X, H = gates[0], gates[1], gates[2]
        order = [
            [None, None, C],
            [H, X, C],
            [None, None, None],
        ]
        self.__check_order(grid, order)

    def test_circuit_grid4(self):
        # shift multi row item regardless of row order (e.g., the second row is shifted explicitly while the first row
        # only shift implicitly)
        grid = RelationalGrid.empty(2, 4)
        gates = [
            MyTestCase.GateDummy(2, "C"),
            MyTestCase.GateDummy(1, "X"),
            MyTestCase.GateDummy(2, "S"),
            MyTestCase.GateDummy(1, "H"),
        ]
        positioning = [
            ([0, 1], 0),
            (1, 0),
            ([0, 1], 0),
            (0, 0),
        ]
        self.__place_in_grid(grid, gates, positioning)

        C, X, S, H = gates[0], gates[1], gates[2], gates[3]
        order = [
            [H, S, None, C],
            [None, S, X, C],
        ]
        self.__check_order(grid, order)


    # todo test len(grid)!


if __name__ == '__main__':
    unittest.main()
