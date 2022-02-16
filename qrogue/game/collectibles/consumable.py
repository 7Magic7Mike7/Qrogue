from abc import ABC, abstractmethod

#from qrogue.game.actors.robot import Robot
from qrogue.game.collectibles.collectible import Collectible, CollectibleType


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

    def default_price(self) -> int:
        # the higher the number of charges the less the additional price (based on harmonic numbers)
        return int(sum([Consumable.__DEFAULT_PRICE / (i+1) for i in range(self._charges)]))

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


class HealthPotion(Consumable):
    def __init__(self, heal_amount: int):
        super(HealthPotion, self).__init__(charges=2)
        self.__amount = heal_amount
        self.__hp_gained = 0
        self.__robot = None

    def on_consumption(self, robot: "Robot") -> bool:
        self.__hp_gained = robot.heal(self.__amount)
        self.__robot = robot
        return True

    def effect_description(self) -> str:
        return f"Healed {self.__robot} by {self.__hp_gained} HP."  # todo change from robot to robot.qubit_set?

    def name(self) -> str:
        return "Health Potion"

    def description(self) -> str:
        return "Heals some HP on consumption."

    def to_string(self) -> str:
        return f"+{self.__amount}HP Potion"

    def __str__(self):
        return self.to_string()
