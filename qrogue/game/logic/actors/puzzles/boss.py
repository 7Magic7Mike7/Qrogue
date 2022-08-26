
from abc import ABC

from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible, Coin

from .enemy import Enemy


class Boss(Enemy, ABC):
    """
    A special Enemy with specified target and reward.
    """

    __BOSS_ID: int = 0

    def __init__(self, target: StateVector, reward: Collectible):
        """
        Creates a boss enemy with a specified target StateVector and a specified reward.

        :param target:
        :param reward:
        """
        super().__init__(Boss.__BOSS_ID, target, reward)
        self.__is_defeated = False

    @property
    def is_defeated(self) -> bool:
        """

        :return: whether the boss has been defeated yet or not
        """
        return self.__is_defeated   # todo why would "is_active" not be sufficient?

    def _on_reached(self):
        self.__is_defeated = True   # todo is this really needed? can't we simply override is_reached()?

    def flee_check(self) -> bool:
        return True


class DummyBoss(Boss):
    def __init__(self):
        stv = StateVector([1, 0, 0, 0, 0, 0, 0, 0])
        super(DummyBoss, self).__init__(stv, Coin(3))
