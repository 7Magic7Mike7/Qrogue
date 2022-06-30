
from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import RandomManager, PuzzleConfig

from .target import Target


class Enemy(Target):
    """
    An Enemy is a Target with a certain chance to flee.
    """

    def __init__(self, eid: int, target: StateVector, reward: Collectible):
        """
        Creates an Enemy-Target with a given target state vector and reward.
        :param eid: id in [0, 9] to calculate certain properties
        :param target: the StateVector to reach
        :param reward: the Collectible to get as a reward
        """
        super().__init__(target, reward)
        self.__id = eid
        self.__rm = RandomManager.create_new()

    def _on_reached(self):
        """
        Nothing to do here.
        :return: None
        """
        pass

    def flee_check(self) -> bool:
        return self.__rm.get(msg="Enemy.flee_check()") < PuzzleConfig.calculate_flee_chance(self.__id)

    def __str__(self):
        return "Enemy " + super(Enemy, self).__str__()
