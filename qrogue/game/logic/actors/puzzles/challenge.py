from typing import List, Tuple, Optional

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, Instruction

from qrogue.game.logic.actors.puzzles import Target
from qrogue.util import CheatConfig, Logger, Config


class Challenge(Target):
    def __init__(self, target: StateVector, reward: Collectible, min_gates: int, max_gates: int,
                 allowed_gates: List[Instruction] = None):
        # allow target and input to be equal since other constraints can still make it challenging
        super().__init__(target, reward, allow_target_input_equality=True)
        self.__min_gates = min_gates
        self.__max_gates = max_gates
        self.__allowed_gates = allowed_gates    # not yet usable!

    @property
    def flee_energy(self) -> int:
        return 10

    @property
    def min_gates(self) -> int:
        return self.__min_gates

    @property
    def max_gates(self) -> int:
        return self.__max_gates

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Optional[Collectible]]:
        # first check if the additional constraints are met
        if state_vector.num_of_used_gates is None:
            Logger.instance().error(f"Challenge.is_reached() got state_vector with no number of used gates specified!",
                                    show=Config.debugging(), from_pycui=False)
            return super(Challenge, self).is_reached(state_vector)  # we cannot check the num_of_gates constraint

        if self.__min_gates <= state_vector.num_of_used_gates <= self.__max_gates or CheatConfig.in_god_mode():
            return super(Challenge, self).is_reached(state_vector)
        return False, None

    def _on_reached(self):
        pass
