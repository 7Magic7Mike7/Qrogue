from abc import ABC

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, Instruction, instruction as gates
from qrogue.util import PuzzleConfig
from .riddle import Riddle


class Boss(Riddle, ABC):
    """
    A special Enemy with specified target and reward.
    """

    __BOSS_ID: int = 0
    # we have to pass a seed to Riddle(), but we don't have instability so its value doesn't matter
    __PLACEHOLDER_SEED = 714985

    def __init__(self, id_: int, target: StateVector, input_: StateVector, reward: Collectible,
                 attempts: int = 10):  # todo: later attempts cannot be optional
        """
        Creates a boss enemy with a list of specified target and input StateVectors and a specified reward.
        :param id_: an integer unique per level to identify the target
        :param puzzles: list of (target stv, input stv)
        :param reward: the reward for winning against the boss
        """
        self.__index = 0

        super().__init__(id_, target, reward, Boss.__PLACEHOLDER_SEED, attempts, input_, stable_probability=0)

    @property
    def flee_energy(self) -> int:
        return PuzzleConfig.BOSS_FLEE_ENERGY

    def _on_reached(self):
        pass    # todo: end level?

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
        super().__init__(0, puzzles[0][0], puzzles[0][1], reward, attempts=5)
