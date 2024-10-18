from typing import Optional

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import PuzzleConfig
from .target import Target


class Enemy(Target):
    """
    An Enemy is a Target with a certain chance to flee.
    """

    def __init__(self, id_: int, eid: int, target: StateVector, reward: Optional[Collectible],
                 input_: Optional[StateVector] = None):
        """
        Creates an Enemy-Target with a given target state vector and reward.
        :param id_: an integer unique per level to identify the target
        :param eid: enemy id in [0, 9] to calculate certain properties
        :param target: the StateVector to reach
        :param reward: the Collectible to get as a reward
        :param input_: the StateVector to start with (all |0> by default)
        """
        super().__init__(id_, target, reward, input_)
        self.__id: int = eid

    @property
    def flee_energy(self) -> int:
        return PuzzleConfig.calculate_flee_energy(self.__id)

    def flee_check(self) -> bool:
        """
        Check if we are allowed to flee or not.

        :return: True if fleeing was a success, False otherwise (currently not possible)
        """
        return True  # self.__rm.get(msg="Enemy.flee_check()") < PuzzleConfig.calculate_flee_chance(self.__id)

    def __str__(self):
        return "Enemy " + super(Enemy, self).__str__()
