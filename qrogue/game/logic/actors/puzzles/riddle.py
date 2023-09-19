from typing import Tuple, Optional

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import RandomManager

from .target import Target


class Riddle(Target):
    """
    A Target with a restricted amount of attempts to reach its StateVector.
    """

    __UNSTABLE_PROBABILITY = 0.65   # todo only for tutorial! Should be 0.5 later

    def __init__(self, target: StateVector, reward: Collectible, attempts: int = 1,
                 input_: Optional[StateVector] = None):
        super().__init__(target, reward, input_)
        self.__attempts = attempts
        self.__rm = RandomManager.create_new()  # todo does this need to be seeded? I think yes for simulations :(
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
            self.__can_attempt = self.__rm.get() < Riddle.__UNSTABLE_PROBABILITY
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

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Optional[Collectible]]:
        success, reward = super(Riddle, self).is_reached(state_vector)
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
