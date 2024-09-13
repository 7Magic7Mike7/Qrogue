from typing import List, Tuple, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible, Instruction
from qrogue.util import CheatConfig, Logger, Config
from .target import Target


class Challenge(Target):
    def __init__(self, id_: int, target: StateVector, min_gates: int, max_gates: Optional[int] = None,
                 reward: Optional[Collectible] = None, allowed_gates: List[Instruction] = None,
                 input_: Optional[StateVector] = None):
        if max_gates < min_gates:
            Logger.instance().error(f"Trying to create a challenge with less max_gates={max_gates} then "
                                    f"min_gates={min_gates}! Using min_gates for both values instead.", show=False,
                                    from_pycui=False)
        if max_gates is None:
            max_gates = min_gates
        # allow target and input to be equal since other constraints can still make it challenging
        super().__init__(id_, target, reward, input_, allow_target_input_equality=True)
        self.__min_gates = min_gates
        self.__max_gates = max_gates
        self.__allowed_gates = allowed_gates  # not yet usable!     # todo: make "mandatory_gates" instead?

    @property
    def flee_energy(self) -> int:
        return 10

    @property
    def min_gates(self) -> int:
        return self.__min_gates

    @property
    def max_gates(self) -> int:
        return self.__max_gates

    def is_reached(self, state_vector: StateVector, circ_matrix: CircuitMatrix) -> Tuple[bool, Optional[Collectible]]:
        # first check if the additional constraints are met
        if circ_matrix.num_of_used_gates is None:
            Logger.instance().error(f"Challenge.is_reached() got state_vector with no number of used gates specified!",
                                    show=Config.debugging(), from_pycui=False)
            # we cannot check the num_of_gates constraint
            return super(Challenge, self).is_reached(state_vector, circ_matrix)

        if self.__min_gates <= circ_matrix.num_of_used_gates <= self.__max_gates or CheatConfig.in_god_mode():
            return super(Challenge, self).is_reached(state_vector, circ_matrix)
        return False, None
