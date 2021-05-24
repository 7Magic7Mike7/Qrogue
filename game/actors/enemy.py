
from game.actors.target import Target
from game.collectibles.collectible import Collectible
from game.logic.qubit import StateVector


class Enemy(Target):
    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        super().__init__(target, reward)
        self.__flee_chance = flee_chance

    @property
    def flee_chance(self):
        return self.__flee_chance

    def __str__(self):
        return "Enemy " + super(Enemy, self).__str__()


class DummyEnemy(Enemy):
    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        super(DummyEnemy, self).__init__(target, reward, flee_chance)
