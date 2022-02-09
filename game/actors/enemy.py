
from game.actors.target import Target
from game.collectibles.collectible import Collectible
from game.logic.qubit import StateVector


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

    def _on_reached(self):
        """
        Nothing to do here.
        :return: None
        """
        pass

    @property
    def flee_chance(self):
        """
        Fleeing gets rid of a Target without having to reach it.
        :return: the probability to succeed at fleeing from this Target
        """
        return self.__flee_chance

    def __str__(self):
        return "Enemy " + super(Enemy, self).__str__()


class DummyEnemy(Enemy):
    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        super(DummyEnemy, self).__init__(target, reward, flee_chance)

    def _on_reached(self):
        pass
