from game.actors.target import Target
from game.collectibles.collectible import Collectible
from game.logic.qubit import StateVector


class Riddle(Target):
    def __init__(self, target: StateVector, reward: Collectible, attempts: int = 1):
        super().__init__(target, reward)
        self.__attempts = attempts

    @property
    def attempts(self) -> int:
        return self.__attempts

    @property
    def is_active(self) -> bool:
        return super(Riddle, self).is_active and self.attempts > 0

    def is_reached(self, state_vector: StateVector) -> bool:
        if not super(Riddle, self).is_reached(state_vector):
            self.__attempts -= 1
            return False
        return True
