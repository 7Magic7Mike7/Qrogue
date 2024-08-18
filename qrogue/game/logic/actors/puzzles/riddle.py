from typing import Tuple, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import RandomManager, CheatConfig
from .target import Target


class Riddle(Target):
    """
    A Target with a restricted amount of edits to reach its StateVector.
    """

    __STABLE_PROBABILITY = 0.5

    def __init__(self, id_: int, target: StateVector, reward: Collectible, seed: int, edits: int = 1,
                 input_: Optional[StateVector] = None, stable_probability: float = __STABLE_PROBABILITY):
        """
        :param stable_probability: how likely it is to stay stable after all edits are used up
            (0=no edits possible, 1=infinitely many additional edits possible)
        """
        super().__init__(id_, target, reward, input_)
        self.__edits = edits
        self.__stable_probability = stable_probability
        self.__rm = RandomManager.create_new(seed)
        self.__can_attempt = True

    @property
    def edits(self) -> int:
        """

        :return: the number of edits that are left for reaching this Target's StateVector
        """
        return self.__edits

    @property
    def can_attempt(self) -> bool:
        if self.edits > 0 or CheatConfig.has_infinite_edits():
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
            self.__edits = max(self.__edits - 1, 0)
            self.__can_attempt = self.can_attempt
        return success, reward
