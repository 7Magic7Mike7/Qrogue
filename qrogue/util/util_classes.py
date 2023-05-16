from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Iterator, Set, TypeVar, Generic


class LinkedList:
    class _Node:
        def __init__(self, val: Any, next_: Optional["LinkedList._Node"] = None):
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


class MyGrid(Generic[T], ABC):
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

    class _MyGridIterator:
        def __init__(self, grid: "MyGrid[T]"):
            self.__grid = grid
            self.__column = 0
            self.__row = 0
            self.__cur_item: Optional[MyGrid.Item[T]] = None

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

    def __init__(self, grid: List[List[Optional["MyGrid.Item[T]"]]]):
        assert len(grid) > 0, "Grid has empty first dimension!"
        assert len(grid[0]) > 0, "Grid has empty second dimension!"
        for i in range(1, len(grid)):
            assert len(grid[i]) == len(grid[0]), "Grid is not rectangular!"

        self.__grid: List[List[Optional[MyGrid.Item[T]]]] = grid
        self.__num_of_rows = len(grid)
        self.__num_of_columns = len(grid[0])

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

    def _validate_row(self, value: int):
        assert 0 <= value < self.num_of_rows, f"Illegal row-index! 0 <= {value} < {self.num_of_rows} is False!"

    def _validate_col(self, value: int):
        assert 0 <= value < self.num_of_columns, f"Illegal col-index! 0 <= {value} < {self.num_of_columns} is False!"

    def _get(self, row: int, col: int) -> Optional[Item[T]]:
        self._validate_row(row)
        self._validate_col(col)
        return self.__grid[row][col]

    def _is_free(self, row: int, col: int) -> bool:
        self._validate_row(row)
        self._validate_col(col)
        return self.__grid[row][col] is None

    def _set(self, row: int, col: int, item: "MyGrid.Item[T]"):
        self._validate_row(row)
        self._validate_col(col)
        self.__grid[row][col] = item

    def _reset(self, row: int, col: int):
        self._validate_row(row)
        self._validate_col(col)
        self.__grid[row][col] = None

    def _raw_copy(self) -> List[List[Optional["MyGrid.Item[T]"]]]:
        return [row.copy() for row in self.__grid]

    @abstractmethod
    def get(self, row: int, column: int) -> "MyGrid.Item[T]":
        pass

    @abstractmethod
    def place(self, item: "MyGrid.Item[T]", column: int, overwrite: bool = True) -> bool:
        """
        :return: True if item was successfully placed, False otherwise
        """
        pass

    @abstractmethod
    def remove(self, item: "MyGrid.Item[T]", reset_qubits: bool = True, reset_position: bool = True) -> bool:
        pass

    @abstractmethod
    def copy(self) -> "MyGrid":
        pass

    def _has_row_free_space(self, row: int) -> bool:
        """
        Whether the given row has still a free spot where we could place an item at.
        """
        for val in self.__grid[row]:
            if val is None:
                return True
        return False

    def first_used_column_in_row(self, row: int) -> int:
        for col in range(self.__num_of_columns):
            item = self.get(row, col)
            if item is not None:
                return col
        return -1   # no item in row

    def clear(self):
        for col in range(self.num_of_columns):
            for row in range(self.num_of_rows):
                item = self.__grid[row][col]
                if item is not None: item.reset()
                self.__grid[row][col] = None

    def __len__(self):
        items: Set["MyGrid.Item[T]"] = set()
        for qu in range(self.__num_of_rows):
            for pos in range(self.__num_of_columns):
                # we have to iterate over all columns since multi row items can create empty spaces
                # in the middle of a row (even though we always shift to the left as far as possible)
                item = self.get(qu, pos)
                if item is not None: items.add(item)
        return len(items)

    def __contains__(self, value):
        for item in self:
            if value == item.value:
                return True
        return False

    def __iter__(self):
        return MyGrid._MyGridIterator(self)

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


class RelationalGrid(MyGrid[T]):
    @staticmethod
    def empty(num_of_rows: int, num_of_columns: int) -> "RelationalGrid[T]":
        grid: List[List[Optional[MyGrid.Item[T]]]] = [[None] * num_of_columns for _ in range(num_of_rows)]
        return RelationalGrid[T](grid)

    def __init__(self, grid: List[List[Optional["MyGrid.Item[T]"]]]):
        # rows have to be left-aligned with respect to their other columns (i.e., no free space is allowed to be in
        # front of a single-row item, but as soon as there is a multi-row item there can be)
        prepared_grid: List[List[Optional[MyGrid.Item[T]]]] = []
        num_of_columns = max([len(row) for row in grid])

        # adapt every row to have the same number of columns
        for row in grid: row += [None] * (num_of_columns - len(row))

        # shift row elements to the left if there is empty space in front
        shift_amount = 0
        for col in range(num_of_columns):
            empty_column = True
            for row in grid:
                if row[col] is not None:
                    empty_column = False
                    break
            if empty_column: shift_amount += 1
            else: break
        if shift_amount == num_of_columns: shift_amount = 0  # no need to shift if everything is empty

        for row in grid: prepared_grid.append(row[shift_amount:].copy() + [None] * shift_amount)

        super().__init__(prepared_grid)

    def copy(self):
        return RelationalGrid[T](self._raw_copy())

    def get(self, row: int, column: int) -> Optional["MyGrid.Item[T]"]:
        return self._get(row, column)

    def __first_free_spot(self, row: int, og_col: int) -> int:
        # search the first free spot in front of og_pos (or og_pos if nothing is free)
        og_col -= 1
        while og_col >= 0 and self._is_free(row, og_col): og_col -= 1
        # we either stopped because there is a gate at og_pos (hence we increase it again) or because og_pos < 0
        return og_col + 1

    def __shift_right(self, row: int, og_col: int) -> int:
        """
        :returns: by how many spots we shifted (0 = no shift needed) or -1 if we cannot shift
        """
        if self._is_free(row, og_col): return 0  # no need to shift

        # find the left most free spot after og_pos
        cur_col = og_col
        while True:
            cur_col += 1
            if cur_col >= self.num_of_columns: return -1  # no free spot to the right
            if self._is_free(row, cur_col): break
        distance = cur_col - og_col

        # now go back to position and shift everything to the right by 1
        while cur_col > og_col:
            shifting_item = self._get(row, cur_col - 1)
            for other_row in shifting_item.row_iter():
                if other_row != row:  # single row items never enter this if
                    # 1. shift everything to the right of shifting_item's other rows
                    # 2. shift the other rows of shifting_item
                    # 3. reset the other rows of shifting_item
                    if self.__shift_right(other_row, cur_col) < 0: return -1
                    self._set(other_row, cur_col, self._get(other_row, cur_col - 1))
                    self._reset(other_row, cur_col - 1)
            self._set(row, cur_col, shifting_item)
            cur_col -= 1
        self._reset(row, og_col)  # reset the value of the original position
        return distance

    def __undo_shift_right(self, row: int, position: int, num_of_shifts: int):
        for i in range(num_of_shifts):
            self._set(row, position + i, self._get(row, position + i + 1))
        self._reset(row, position + num_of_shifts)

    def place(self, item: "MyGrid.Item[T]", column: int, overwrite: bool = True) -> bool:
        self.remove(item, reset_qubits=False)

        qubit = item.row_copy()
        if isinstance(qubit, int): qubit = [qubit]
        assert len(qubit) == item.num_of_rows

        for qu in qubit:
            if not self._has_row_free_space(qu):
                return False

        left_most_positions = [self.__first_free_spot(qu, column) for qu in qubit]
        nums_of_shifts = []
        position = max(left_most_positions)
        for i, qu in enumerate(qubit):
            num_of_shifts = self.__shift_right(qu, position)
            if num_of_shifts < 0:
                for j, qq in enumerate(qubit[:i]): self.__undo_shift_right(qq, position, nums_of_shifts[j])
                return False
            else:
                nums_of_shifts.append(num_of_shifts)
            self._set(qu, position, item)

        return True

    def remove(self, item: "MyGrid.Item[T]", reset_qubits: bool = True, reset_position: bool = True) -> bool:
        place_data: List[Optional[int]] = []
        removal_failed = False
        for qubit in item.row_iter():
            position = None
            for pos in range(self.num_of_columns):
                val = self._get(qubit, pos)
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
                self._reset(qu, pos)
            item.reset(skip_rows=not reset_qubits, skip_column=not reset_position)
            return True

    def clear(self):
        pass
