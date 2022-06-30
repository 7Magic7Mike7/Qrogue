
from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import RandomManager

from .target import Target


class Enemy(Target):
    """
    An Enemy is a Target with a certain chance to flee.
    """

    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        """
        Creates an Enemy-Target with a given target state vector, a reward and a certain chance to flee.
        :param target: the StateVector to reach
        :param reward: the Collectible to get as a reward
        :param flee_chance: how likely it is for the player to flee from this Target
        """
        super().__init__(target, reward)
        self.__flee_chance = flee_chance
        self.__rm = RandomManager.create_new()

    def _on_reached(self):
        """
        Nothing to do here.
        :return: None
        """
        pass

    def flee_check(self) -> bool:
        return self.__rm.get(msg="Enemy.flee_check()") < self.__flee_chance

    def __str__(self):
        return "Enemy " + super(Enemy, self).__str__()
