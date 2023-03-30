from typing import Any, Optional, List, Union


class LinkedList:
    class _Node:
        def __init__(self, val: Any, next_: Optional["_Node"] = None):
            self.val = val
            self.next = next_

        def __str__(self):
            if self.next is None:
                return f"{self.val} -> None"
            else:
                return f"{self.val} -> {self.next.val}"

    def __init__(self, content: Optional[List] = None, capacity: Optional[int] = None):
        if capacity is None:
            capacity = -1

        self.__head = None
        self.__size = 0
        self.__capacity = capacity

        if content is not None:
            cur = None
            for val in content:
                if self.is_full:
                    break
                if self.__head is None:
                    self.__head = LinkedList._Node(val)
                    cur = self.__head
                else:
                    prev = cur
                    cur = LinkedList._Node(val)
                    prev.next = cur

                self.__size += 1

    @property
    def is_empty(self) -> bool:
        return self.__head is None

    @property
    def is_full(self) -> bool:
        if self.__capacity < 0:
            return False
        else:
            return self.__size >= self.__capacity

    def insert(self, val: Any, pos: int) -> bool:
        assert val is not None, "Not allowed to insert None!"
        assert 0 <= pos, f"pos={pos} needs to be a positive integer!"

        if self.is_full:
            return False

        if pos == 0 or self.__head is None:
            # insert new value as head
            temp = LinkedList._Node(val, self.__head)
            self.__head = temp
        else:
            # find position we want to insert it at or insert it at the end
            i, prev, cur = 1, self.__head, self.__head.next
            while i < pos and cur is not None:
                prev = cur
                cur = cur.next
                i += 1
            prev.next = LinkedList._Node(val, cur)

        self.__size += 1
        return True

    def remove(self, val: Any) -> bool:
        if val == self.__head.val:
            self.__head = self.__head.next
            self.__size -= 1
            return True

        prev, cur = self.__head, self.__head.next
        while True:
            if cur is None:
                return False
            elif cur.val == val:
                break
            prev = cur
            cur = cur.next

        prev.next = cur.next    # jump over cur to remove it
        self.__size -= 1
        return True

    def get(self, index: int) -> Optional[Any]:
        assert 0 <= index, f"index={index} needs to be a positive integer!"

        if index >= self.__size:
            return None     # out of range

        i, cur = 0, self.__head
        while i < index and cur.next is not None:
            cur = cur.next
            i += 1

        if cur is None: return None     # todo think through why this can happen
        return cur.val

    def clear(self):
        self.__head = None

    def __len__(self):
        return self.__size

    def __iter__(self):
        return _LinkedListIterator(self)

    def __contains__(self, item):
        for elem in self:
            if elem == item:
                return True
        return False

    def __str__(self):
        text = "LinkedList("
        connector = " -> "
        cur = self.__head
        while cur is not None:
            text += f"{cur.val}{connector}"
            cur = cur.next
        return f"{text}None)"   # last element points to None


class _LinkedListIterator:
    """
    Allows us to easily iterate through our LinkedList.
    """

    def __init__(self, linked_list: LinkedList):
        self.__index: int = 0
        self.__linked_list: LinkedList = linked_list

    def __next__(self) -> Any:
        if self.__index < len(self.__linked_list):
            item = self.__linked_list.get(self.__index)
            self.__index += 1
            return item
        raise StopIteration


class GateDummy:
    def __init__(self, needed_qubits: int, character: str):
        self.qargs: List[int] = []
        self.needed_qubits: int = needed_qubits
        self.character = character[0]

    def __str__(self):
        return f"{self.character} ({self.qargs})"


class CircuitGrid:
    def __init__(self, num_of_qubits: int, circuit_space: int):
        self.__num_of_qubits = num_of_qubits    # num of rows
        self.__circuit_space = circuit_space    # num of columns

        # rows have to be left-aligned with respect to their other qubits (i.e., no free space is allowed to be in
        # front of a single qubit gate)
        self.__grid: List[List[Optional[GateDummy]]] = [[None] * circuit_space for _ in range(num_of_qubits)]

    def __remove(self, gate: GateDummy) -> bool:
        positions: List[Optional[int]] = []
        removal_failed = False
        for qubit in gate.qargs:
            position = None
            for pos in range(self.__circuit_space):
                val = self.__grid[qubit][pos]
                if val == gate:
                    position = pos
                    break
            removal_failed = removal_failed or position is None     # once True, will stay True
            positions.append(position)

        if removal_failed:
            return False
        else:
            for i, pos in enumerate(positions):
                self.__grid[gate.qargs[i]][pos] = None
            return True

    def _qubit_row(self, qubit: int) -> List[Optional[GateDummy]]:
        assert 0 <= qubit < len(self.__grid)
        return self.__grid[qubit]

    def _num_of_gates_on_qubit(self, qubit: int) -> int:
        count = 0
        for val in self._qubit_row(qubit):
            if val is not None:
                count += 1
        return count

    def _gate_at(self, qubit: int, position: int, relative: bool = True) -> Optional[GateDummy]:
        if relative:
            assert 0 <= position < self._num_of_gates_on_qubit(qubit)
            count = -1
            for val in self._qubit_row(qubit):
                if val is not None:
                    count += 1
                    if position == count:
                        return val
            return None
        else:
            assert 0 <= position < len(self._qubit_row(qubit))
            return self.__grid[qubit][position]

    def _find_pos_for(self, qubit: int, og_position: int):
        row = self.__grid[qubit]
        if og_position == 0:
            pass
        while True:
            pass

    def _has_qubit_free_space(self, qubit: int) -> bool:
        """
        Whether the given qubit (i.e., grid row) has still a free spot where we could place a gate at.
        """
        free_spaces = 0
        for val in self.__grid[qubit]:
            if val is None:
                free_spaces += 1
        return free_spaces > 0

    def get(self, qubit: int, position: int) -> Optional[GateDummy]:
        assert 0 <= qubit < self.__num_of_qubits, \
            f"Invalid qubit value: 0 <= {qubit} <= {self.__num_of_qubits} is False!"
        assert 0 <= position < self.__circuit_space, \
            f"Invalid qubit value: 0 <= {position} <= {self.__circuit_space} is False!"

        return self.__grid[qubit][position]

    def place(self, gate: GateDummy, qubit: Union[int, List[int]], position: int) -> bool:
        self.__remove(gate)

        if isinstance(qubit, int): qubit = [qubit]
        assert len(qubit) == gate.needed_qubits

        for qu in qubit:
            if not self._has_qubit_free_space(qu):
                return False

        def first_free_spot(qubit_: int, og_pos: int) -> int:
            # search the first free spot in front of og_pos (or og_pos if nothing is free)
            og_pos -= 1
            while og_pos >= 0 and self.__grid[qubit_][og_pos] is None: og_pos -= 1
            # we either stopped because there is a gate at og_pos (hence we increase it again) or because og_pos < 0
            return og_pos + 1

        def shift_right(qubit_: int, og_pos: int):
            if self.__grid[qubit_][og_pos] is None:
                return  # no need to shift

            # find the left most free spot after og_pos
            index = og_pos + 1
            while index < self.__circuit_space and self.__grid[qubit_][index] is not None: index += 1
            # now go back to position and shift everything to the right by 1
            while index > og_pos:
                self.__grid[qubit_][index] = self.__grid[qubit_][index - 1]
                index -= 1

        if gate.needed_qubits == 1:
            qubit = qubit[0]
            if self.__grid[qubit][position] is None:
                # no need to shift anything since no gate will be to the right
                position = first_free_spot(qubit, position)    # align it to the left by finding the left most viable position
            shift_right(qubit, position)    # does nothing if the corresponding spot is free
            self.__grid[qubit][position] = gate
            return True
        else:
            left_most_positions = [first_free_spot(qu, position) for qu in qubit]
            position = max(left_most_positions)
            for qu in qubit:
                shift_right(qu, position)               # todo cannot shift multi-qubit gates yet!
                self.__grid[qu][position] = gate

    def __str__(self):
        text = ""
        for row in self.__grid:
            for val in row:
                if val is None:
                    text += "---"
                else:
                    text += f"-{val.character}-"
            text += "\n"
        return text
