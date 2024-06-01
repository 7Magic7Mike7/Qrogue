from typing import Tuple, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import RandomManager
from .target import Target


class Riddle(Target):
    """
    A Target with a restricted amount of attempts to reach its StateVector.
    """

    __STABLE_PROBABILITY = 0.5

    def __init__(self, id_: int, target: StateVector, reward: Collectible, seed: int, attempts: int = 1,
                 input_: Optional[StateVector] = None, stable_probability: float = __STABLE_PROBABILITY):
        """
        :param stable_probability: how likely it is to stay stable after all attempts are used up
            (0=no additional attempts possible, 1=infinitely many additional attempts possible)
        """
        super().__init__(id_, target, reward, input_)
        self.__attempts = attempts
        self.__stable_probability = stable_probability
        self.__rm = RandomManager.create_new(seed)
        self.__can_attempt = True

    @property
    def attempts(self) -> int:
        """

        :return: the number of attempts that are left for reaching this Target's StateVector
        """
        return self.__attempts

    @property
    def can_attempt(self) -> bool:
        if self.attempts > 0:
            self.__can_attempt = True
        else:
            self.__can_attempt = self.__rm.get() < self.__stable_probability
        return self.__can_attempt

    @property
    def is_active(self) -> bool:
        return super(Riddle, self).is_active and self.__can_attempt

    @property
    def flee_energy(self) -> int:
        """
        Fleeing (pausing) Riddles should always be possible, hence it costs 0 energy.

        :return: 0
        """
        return 0

    def is_reached(self, state_vector: StateVector, circ_matrix: CircuitMatrix) -> Tuple[bool, Optional[Collectible]]:
        success, reward = super(Riddle, self).is_reached(state_vector, circ_matrix)
        if success:
            assert reward is not None  # riddles always need to give a reward
        else:
            self.__attempts = max(self.__attempts - 1, 0)
            self.__can_attempt = self.can_attempt
        return success, reward

    def _on_reached(self):
        """
        Nothing additional to do for reached Riddles.
        :return: None
        """
        pass
