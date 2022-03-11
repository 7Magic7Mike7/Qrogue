
from qrogue.game.logic.collectibles import Collectible, CollectibleType


class Qubit(Collectible):
    __MIN_NUM = 1
    __MAX_NUM = 3

    def __init__(self, num: int = 1):
        if self.__MIN_NUM <= num <= self.__MAX_NUM:
            super().__init__(CollectibleType.Qubit)
            self.__num = num
        else:
            raise ValueError(f"Error trying to add to many qubits: {num}! Only between {self.__MIN_NUM} and "
                             f"{self.__MAX_NUM} allowed at once.")

    @property
    def additional_qubits(self) -> int:
        return self.__num

    def name(self) -> str:
        return "Qubit"

    def description(self) -> str:
        return "Qubits are the essence of any circuit you create."

    def default_price(self) -> int:
        return 100  # currently the plan is to not have it in shops

    def to_string(self) -> str:
        return f"Qubit ({self.additional_qubits})"
