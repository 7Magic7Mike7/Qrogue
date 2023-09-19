
from abc import ABC
from typing import Tuple, List, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible, Coin
from qrogue.util import PuzzleConfig

from .target import Target


class Boss(Target, ABC):
    """
    A special Enemy with specified target and reward.
    """

    __BOSS_ID: int = 0

    def __init__(self, puzzles: List[Tuple[StateVector, StateVector]], reward: Collectible):
        """
        Creates a boss enemy with a list of specified target and input StateVectors and a specified reward.

        :param puzzles: list of (target stv, input stv)
        :param reward:
        """
        self.__puzzles = puzzles
        self.__index = 0

        super().__init__(lambda: self.__puzzles[self.__index][0], reward, lambda: self.__puzzles[self.__index][1])

    @property
    def flee_energy(self) -> int:
        return PuzzleConfig.BOSS_FLEE_ENERGY

    @property
    def index(self) -> int:
        return self.__index

    def is_reached(self, state_vector: StateVector, circ_matrix: CircuitMatrix) -> Tuple[bool, Optional[Collectible]]:
        # the last index we need to check is either the one before self.__index or the very last possible index
        end_index = self.__index - 1 if self.__index > 0 else len(self.__puzzles) - 1
        reward = None
        while self.__index != end_index:    # todo this way we do not necessarily see the different puzzles
            res, reward = super().is_reached(state_vector, circ_matrix)

            # update index (+ start again at 0 if we would get out of bounds)
            self.__index += 1
            if self.__index >= len(self.__puzzles):
                self.__index = 0

            # return False if the current puzzle was not reached
            if not res: return False, None
            # otherwise continue with next puzzle

        # if the loop stopped than every puzzle was solved correctly
        return True, reward

    def _on_reached(self):
        pass

    def flee_check(self) -> bool:
        return True


class DummyBoss(Boss):
    def __init__(self):
        stv = StateVector([1, 0, 0, 0, 0, 0, 0, 0], num_of_used_gates=0)
        super(DummyBoss, self).__init__(stv, Coin(3))
