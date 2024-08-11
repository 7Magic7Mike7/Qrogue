from typing import Tuple, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible

from .target import Target


class FusionTarget(Target):
    def __init__(self, num_of_qubits: int):
        super().__init__(id_=0, target=StateVector.create_zero_state_vector(num_of_qubits), reward=None)

    def is_reached(self, state_vector: StateVector, circ_matrix: CircuitMatrix) -> Tuple[bool, Optional[Collectible]]:
        return False, None  # since we just mock a target, we can claim to never reach it
