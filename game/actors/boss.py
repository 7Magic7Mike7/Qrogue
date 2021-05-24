
from abc import abstractmethod, ABC
from game.actors.enemy import Enemy
from game.collectibles.collectible import Collectible
from game.collectibles.pickup import Coin
from game.logic.qubit import StateVector


class Boss(Enemy, ABC):
    def __init__(self, target: StateVector, reward: Collectible):
        super().__init__(target, reward, flee_chance=0.3)
        self.__is_defeated = False

    @property
    def is_defeated(self) -> bool:
        return self.__is_defeated

    def _on_reached(self):
        self.__is_defeated = True


class DummyBoss(Boss):
    def __init__(self):
        stv = StateVector([1, 0, 0, 0, 0, 0, 0, 0])
        super(DummyBoss, self).__init__(stv, Coin(3))
