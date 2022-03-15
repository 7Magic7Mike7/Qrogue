from typing import Tuple

from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible

from .target import Target


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

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Collectible]:
        success, reward = super(Riddle, self).is_reached(state_vector)
        if not success:
            self.__attempts -= 1
        return success, reward

    def _on_reached(self):
        pass
