from typing import Any, Optional, List


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
