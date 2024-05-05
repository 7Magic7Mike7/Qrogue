from abc import ABC, abstractmethod
from typing import Optional, Callable

# from qrogue.game.actors.robot import Robot
from qrogue.game.logic.collectibles import Collectible, CollectibleType


class Consumable(Collectible, ABC):
    __DEFAULT_PRICE = 7

    def __init__(self, charges: int = 1):
        super(Consumable, self).__init__(CollectibleType.Consumable)
        self._charges = charges

    def charges_left(self) -> int:
        return self._charges

    def consume(self, robot: "Robot") -> bool:
        if self.on_consumption(robot):
            self._charges -= 1
            return True
        return False

    @abstractmethod
    def on_consumption(self, robot: "Robot") -> bool:
        """

        :param robot: the robot that consumed this Consumable
        :return: whether we could successfully consume a charge or not
        """
        pass

    @abstractmethod
    def effect_description(self) -> str:
        pass


class EnergyRefill(Consumable):
    def __init__(self, refill_amount: int = 10):
        super(EnergyRefill, self).__init__(charges=2)
        self.__amount = refill_amount
        self.__amount_refilled = 0
        self.__robot = None

    def on_consumption(self, robot: "Robot") -> bool:
        self.__amount_refilled = robot.increase_energy(self.__amount)
        self.__robot = robot
        return True

    def effect_description(self) -> str:
        return f"Refilled {self.__robot}'s energy by {self.__amount_refilled}."

    def name(self) -> str:
        return "Energy Refill"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Refills some energy of a robot on usage."

    def to_string(self) -> str:
        return f"+{self.__amount} Energy Refill"

    def __str__(self):
        return self.to_string()
