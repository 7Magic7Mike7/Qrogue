from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Iterator, Set, TypeVar, Generic


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


T = TypeVar('T')


class RelationalGrid(Generic[T]):
    class Item(Generic[T], ABC):
        def __init__(self, value: T):
            self.__val = value

        @property
        def value(self) -> T:
            return self.__val

        @property
        @abstractmethod
        def num_of_rows(self) -> int:
            pass

        @abstractmethod
        def row_iter(self) -> Iterator[int]:
            pass

        @abstractmethod
        def row_copy(self) -> List[int]:
            pass

        @abstractmethod
        def reset(self, skip_rows: bool = False, skip_column: bool = False):
            pass

    class _RelationalGridIterator:
        def __init__(self, grid: "RelationalGrid[T]"):
            self.__grid = grid
            self.__column = 0
            self.__row = 0
            self.__cur_item: Optional[RelationalGrid.Item[T]] = None

        def __next__(self) -> T:
            while self.__column < self.__grid.num_of_columns:
                while self.__row < self.__grid.num_of_rows:
                    data = self.__grid.get(self.__row, self.__column)
                    self.__row += 1  # proceed to next qubit

                    # for multi-row items we have to make sure to not return the same again
                    # doesn't work for three rows yet! E.g.: CX @q0, H @q1, CX @q2        # todo use set() instead of single value?
                    if data is not None and data != self.__cur_item:
                        self.__cur_item = data
                        return self.__cur_item.value

                self.__row = 0      # reset row since we are done with the current column
                self.__column += 1  # proceed to next column
            raise StopIteration

    @staticmethod
    def empty(num_of_rows: int, num_of_columns: int) -> "RelationalGrid[T]":
        grid: List[List[Optional[RelationalGrid.Item[T]]]] = [[None] * num_of_columns for _ in range(num_of_rows)]
        return RelationalGrid[T](grid)

    def __init__(self, grid: List[List[Optional["RelationalGrid.Item[T]"]]]):
        # rows have to be left-aligned with respect to their other columns (i.e., no free space is allowed to be in
        # front of a single-row item, but as soon as there is a multi-row item there can be)
        self.__grid: List[List[Optional[RelationalGrid.Item[T]]]] = []
        self.__num_of_rows = len(grid)
        self.__num_of_columns = max([len(row) for row in grid])

        # adapt every row to have the same number of columns
        for row in grid: row += [None] * (self.__num_of_columns - len(row))

        # shift row elements to the left if there is empty space in front
        shift_amount = 0
        for col in range(self.__num_of_columns):
            empty_column = True
            for row in range(self.__num_of_rows):
                if grid[row][col] is not None:
                    empty_column = False
                    break
            if empty_column: shift_amount += 1
            else: break
        if shift_amount == self.__num_of_columns: shift_amount = 0  # no need to shift if everything is empty

        for row in grid: self.__grid.append(row[shift_amount:].copy() + [None] * shift_amount)

    @property
    def num_of_rows(self) -> int:
        return self.__num_of_rows

    @property
    def num_of_columns(self) -> int:
        return self.__num_of_columns

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    @property
    def is_full(self) -> bool:
        for row in range(self.__num_of_rows):
            if self._has_row_free_space(row):
                return False
        return True

    def copy(self):
        return RelationalGrid[T](self.__grid)

    def remove(self, item: "RelationalGrid.Item[T]", reset_qubits: bool = True, reset_position: bool = True) -> bool:
        place_data: List[Optional[int]] = []
        removal_failed = False
        for qubit in item.row_iter():
            position = None
            for pos in range(self.__num_of_columns):
                val = self.__grid[qubit][pos]
                if val == item:
                    position = (qubit, pos)
                    break
            removal_failed = removal_failed or position is None  # once True, will stay True
            place_data.append(position)

        if removal_failed:
            return False
        else:
            for i, data in enumerate(place_data):
                qu, pos = data
                self.__grid[qu][pos] = None
            item.reset(skip_rows=not reset_qubits, skip_column=not reset_position)
            return True

    def first_used_column_in_row(self, row: int) -> int:
        for col in range(self.__num_of_columns):
            item = self.get(row, col)
            if item is not None:
                return col
        return -1   # no item in row

    def _has_row_free_space(self, row: int) -> bool:
        """
        Whether the given row has still a free spot where we could place an item at.
        """
        for val in self.__grid[row]:
            if val is None:
                return True
        return False

    def get(self, row: int, column: int) -> Optional["RelationalGrid.Item[T]"]:
        assert 0 <= row < self.__num_of_rows, \
            f"Row out of bounds: 0 <= {row} < {self.__num_of_rows} is False!"
        assert 0 <= column < self.__num_of_columns, \
            f"Position out of bounds: 0 <= {column} < {self.__num_of_columns} is False!"

        return self.__grid[row][column]

    def find(self, item: "RelationalGrid.Item[T]") -> Tuple[int, List[int]]:
        """
        :return: Tuple of column and rows or (-1, []) if the item was not found
        """
        rows = []
        # for every position we check if gate uses one or more qubits
        for pos in range(self.__num_of_columns):
            for qu in range(self.__num_of_rows):
                found_gate = self.get(qu, pos)
                if found_gate is item:
                    rows.append(qu)
            if len(rows) > 0:
                assert len(rows) == item.num_of_rows, "Not all rows seem to be at the same column!"
                return pos, rows
        return -1, []

    def place(self, item: "RelationalGrid.Item[T]", position: int, overwrite: bool = True) -> bool:
        self.remove(item, reset_qubits=False)

        qubit = item.row_copy()
        if isinstance(qubit, int): qubit = [qubit]
        assert len(qubit) == item.num_of_rows

        for qu in qubit:
            if not self._has_row_free_space(qu):
                return False

        def first_free_spot(qubit_: int, og_pos: int) -> int:
            # search the first free spot in front of og_pos (or og_pos if nothing is free)
            og_pos -= 1
            while og_pos >= 0 and self.__grid[qubit_][og_pos] is None: og_pos -= 1
            # we either stopped because there is a gate at og_pos (hence we increase it again) or because og_pos < 0
            return og_pos + 1

        def shift_right(row_: int, og_col: int) -> bool:
            """
            :returns: True if we successfully shifted, False if it is not possible to shift
            """
            if self.__grid[row_][og_col] is None: return True  # no need to shift

            # find the left most free spot after og_pos
            cur_col = og_col + 1
            while self.__grid[row_][cur_col] is not None:
                cur_col += 1
                if cur_col >= self.__num_of_columns: return False     # no free spot to the right

            # now go back to position and shift everything to the right by 1
            while cur_col > og_col:
                shifting_item = self.__grid[row_][cur_col - 1]
                for other_row in shifting_item.row_iter():
                    if other_row != row_:     # single row items never enter this if
                        # 1. shift everything to the right of shifting_item's other rows
                        # 2. shift the other rows of shifting_item
                        # 3. reset the other rows of shifting_item
                        if not shift_right(other_row, cur_col): return False
                        self.__grid[other_row][cur_col] = self.__grid[other_row][cur_col - 1]
                        self.__grid[other_row][cur_col - 1] = None
                self.__grid[row_][cur_col] = shifting_item
                cur_col -= 1
            self.__grid[row_][og_col] = None  # reset the value of the original position
            return True

        left_most_positions = [first_free_spot(qu, position) for qu in qubit]
        position = max(left_most_positions)
        for qu in qubit:
            shift_right(qu, position)
            self.__grid[qu][position] = item

        return True

    def replace(self, placed_gate: "RelationalGrid.Item[T]", new_gate: "RelationalGrid.Item[T]") -> bool:
        pos, qargs = self.find(placed_gate)
        if 0 <= pos < self.__num_of_columns:
            pass        # todo doesn't work as I planned (I think) because _WrapperGate has 1 qubit but the new_gate can have multiple
        return False

    def clear(self):
        pass

    def __len__(self):
        # todo test method!
        gates: Set["RelationalGrid.Item[T]"] = set()
        for qu in range(self.__num_of_rows):
            for pos in range(self.__num_of_columns):
                # we have to iterate over the whole circuit space since multi qubit gates can create empty spaces
                # in the middle of a row (even though we always shift to the left as far as possible)
                gates.add(self.get(qu, pos))
        return len(gates)

    def __iter__(self):
        return RelationalGrid._RelationalGridIterator(self)

    def __str__(self):
        text = ""
        for row in self.__grid:
            for val in row:
                if val is None:
                    text += "---"
                else:
                    text += f"-{val}-"
            text += "\n"
        return text

