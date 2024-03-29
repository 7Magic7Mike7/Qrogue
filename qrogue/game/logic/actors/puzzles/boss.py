
from abc import ABC
from typing import Tuple, List, Optional

from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Collectible, Score, Instruction, instruction as gates
from qrogue.util import PuzzleConfig

from .target import Target


class Boss(Target, ABC):
    """
    A special Enemy with specified target and reward.
    """

    __BOSS_ID: int = 0

    def __init__(self, id_: int, puzzles: List[Tuple[StateVector, StateVector]], reward: Collectible,
                 static_gate: Optional[Instruction] = None):
        """
        Creates a boss enemy with a list of specified target and input StateVectors and a specified reward.
        :param id_: an integer unique per level to identify the target
        :param puzzles: list of (target stv, input stv)
        :param reward: the reward for winning against the boss
        :param static_gate: an optional gate statically placed in the middle of the robot's circuit
        """
        self.__puzzles = puzzles
        self.__static_gate = static_gate
        self.__index = 0

        if self.__static_gate is not None:
            for i in range(self.__static_gate.num_of_qubits):
                self.__static_gate.use_qubit(i)

        super().__init__(id_, lambda: self.__puzzles[self.__index][0], reward, lambda: self.__puzzles[self.__index][1])

    @property
    def flee_energy(self) -> int:
        return PuzzleConfig.BOSS_FLEE_ENERGY

    @property
    def index(self) -> int:
        return self.__index

    @property
    def puzzles(self) -> List[Tuple[StateVector, StateVector]]:
        return self.__puzzles.copy()

    @property
    def static_gate(self) -> Optional[Instruction]:
        return self.__static_gate

    def is_reached(self, state_vector: StateVector, circ_matrix: CircuitMatrix) -> Tuple[bool, Optional[Collectible]]:
        end_index = self.__index
        reward = None
        while self.__index != end_index or reward is None:    # todo this way we do not see the different puzzles if the player solves it in less steps than the number of puzzles
            res, reward = super().is_reached(state_vector, circ_matrix)
            # return False if the current puzzle was not reached
            if not res:
                return False, None
            # otherwise continue with next puzzle
            # update index (+ start again at 0 if we would get out of bounds)
            self.__index += 1
            if self.__index >= len(self.__puzzles):
                self.__index = 0

        # if the loop stopped than every puzzle was solved correctly
        return True, reward

    def _on_reached(self):
        pass

    def flee_check(self) -> bool:
        return True


class DummyBoss(Boss):
    def __init__(self):
        # needs the player to implement a SwapGate
        puzzles = [
            (Instruction.compute_stv([gates.XGate().setup([0])], 2),
             Instruction.compute_stv([gates.XGate().setup([1])], 2)),
            (Instruction.compute_stv([gates.XGate().setup([1])], 2),
             Instruction.compute_stv([gates.XGate().setup([0])], 2)),
        ]
        super(DummyBoss, self).__init__(puzzles, Score(1000))


class AntiEntangleBoss(Boss):
    def __init__(self, reward: Collectible):
        comb_gate = gates.CombinedGates([
            gates.HGate().setup([0]), gates.CXGate().setup([0, 1]), gates.XGate().setup([0])
        ], 2, label="Anti Entanglement").setup([0, 1])
        target1 = Instruction.compute_stv([comb_gate], 2)
        target2 = Instruction.compute_stv([comb_gate, gates.XGate().setup([0])], 2)
        basis_states = StateVector.create_basis_states(num_of_qubits=2)
        puzzles = [
            (target1, basis_states[0]),
            (target1, basis_states[1]),
            (target2, basis_states[2]),
            (target2, basis_states[3]),
        ]
        super().__init__(0, puzzles, reward)
