from typing import Tuple, Optional

from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible

from .target import Target


class Riddle(Target):
    """
    A Target with a restricted amount of attempts to reach its StateVector.
    """

    def __init__(self, target: StateVector, reward: Collectible, attempts: int = 1):
        super().__init__(target, reward)
        self.__attempts = attempts

    @property
    def attempts(self) -> int:
        """

        :return: the number of attempts that are left for reaching this Target's StateVector
        """
        return self.__attempts

    @property
    def is_active(self) -> bool:
        return super(Riddle, self).is_active and self.attempts > 0

    @property
    def flee_energy(self) -> int:
        """
        Fleeing (pausing) Riddles should always be possible, hence it costs 0 energy.

        :return: 0
        """
        return 0

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Optional[Collectible]]:
        success, reward = super(Riddle, self).is_reached(state_vector)
        if success:
            assert reward is not None  # riddles always need to give a reward
        else:
            self.__attempts -= 1
        return success, reward

    def _on_reached(self):
        """
        Nothing additional to do for reached Riddles.
        :return: None
        """
        pass
