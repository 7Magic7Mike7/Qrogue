from typing import Optional, Callable

from .collectible import Collectible, CollectibleType


class QuantumFuser(Collectible):
    def __init__(self, num: int = 1):
        super().__init__(CollectibleType.QuantumFuser)
        self.__num = num

    def name(self) -> str:
        return "QuantumFuser"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return f"A {self.name()} allows you to fuse multiple gates into a new one."

    def to_string(self) -> str:
        if self.__num == 1:
            return self.name()
        return f"QuantumFuser #{self.__num}"
