from abc import ABC, abstractmethod

from game.actors.player import Player
from game.logic.difficulty import Difficulty, DummyDifficulty
from game.logic.qubit import StateVector


class Enemy(ABC):
    def __init__(self, difficulty: Difficulty):
        self.__difficulty = difficulty
        self.__target = None
        self.__alive = True

    @property
    def target(self) -> "list of numbers":
        if self.__target is None:
            raise Exception("Illegal call! Target not initialized yet.")
        return self.__target.to_value()

    @abstractmethod
    def get_img(self):
        pass

    def _on_death(self):
        self.__alive = False

    def fight_init(self, player: Player):
        self.__target = self.__difficulty.create_statevector(player.num_of_qubits)

    def get_statevector(self) -> StateVector:
        return self.__target

    def damage(self, state_vec: StateVector):
        if self.__target.is_equal_to(state_vec):
            self._on_death()
            return True
        return False

    def is_alive(self):
        return self.__alive

    def __str__(self):
        string = "Enemy ["
        for q in self.__target.to_value():
            string += f"{q} "
        string += "]"
        return string


class DummyEnemy(Enemy):
    def __init__(self, difficulty: Difficulty = DummyDifficulty()):
        super(DummyEnemy, self).__init__(difficulty)

    def get_img(self):
        return "E"
