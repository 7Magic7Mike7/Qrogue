from typing import List, Union, Tuple

from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, Score
from qrogue.util import Logger, MyRandom


class StvDifficulty:
    def __init__(self, num_of_instructions: int):
        self.__num_of_instructions = num_of_instructions

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        """
        Creates a random StateVector that is reachable for the given Robot.

        :param robot: provides the needed information regarding the number of qubits and usable Instructions for
        creating a StateVector
        :param rm: seeded randomness for choosing Instructions and the Qubit(s) to use them on
        :return: a StateVector reachable for the provided Robot
        """
        num_of_qubits = robot.num_of_qubits

        # choose random circuits on random qubits and cbits
        instruction_pool = robot.get_available_instructions()
        instructions = []
        num_of_instructions = min(self.__num_of_instructions, robot.circuit_space)
        for i in range(num_of_instructions):
            qubits = list(range(num_of_qubits))
            # remove = len(instruction_pool) - (self.__num_of_instructions - i) >= 0
            # if not remove:
            #     Logger.instance().throw(Exception(
            #         "this should always remove because else we would duplicate instructions"))
            instruction = rm.get_element(instruction_pool, remove=True, msg="StvDiff_selectInstruction")
            while instruction.use_qubit(rm.get_element(qubits, remove=True, msg="StvDiff_selectQubit")):
                pass
            instructions.append(instruction)
        return Instruction.compute_stv(instructions, num_of_qubits)


class ExplicitStvDifficulty(StvDifficulty):
    def __init__(self, pool: List[StateVector], ordered: bool = False):
        super().__init__(num_of_instructions=-1)
        self.__pool = pool
        self.__ordered = ordered
        self.__order_index = -1

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        if self.__ordered or rm is None:
            self.__order_index += 1
            if self.__order_index >= len(self.__pool):
                self.__order_index = 0
            stv = self.__pool[self.__order_index]
        else:
            stv = rm.get_element(self.__pool, msg="ExplicitStvDiff_selectStv")

        if stv.num_of_qubits != robot.num_of_qubits:
            Logger.instance().error(f"Stv (={stv}) from pool does not have correct number of qubits (="
                                    f"{robot.num_of_qubits})!", show=False, from_pycui=False)
        return stv

    def copy_pool(self) -> List[StateVector]:
        return self.__pool.copy()


class TargetDifficulty(StvDifficulty):
    """
    A class that handles all parameters that define the difficulty of target of a fight.
    """

    @staticmethod
    def dummy() -> "TargetDifficulty":
        return TargetDifficulty(2, [Score(50), Score(100)])

    def __init__(self, num_of_instructions: int, rewards: Union[List[Collectible], CollectibleFactory]):
        """

        :param num_of_instructions: number of Instructions used to create a target StateVector
        :param rewards: either a list of Collectibles or a CollectibleFactory for creating a reward when reaching
        a Target
        """
        super().__init__(num_of_instructions)
        if isinstance(rewards, list):
            self.__reward_factory = CollectibleFactory(rewards)
        elif isinstance(rewards, CollectibleFactory):
            self.__reward_factory = rewards
        else:
            Logger.instance().throw(ValueError(
                "rewards must be either a list of Collectibles or a CollectibleFactory"))

    def produce_reward(self, rm: MyRandom):
        return self.__reward_factory.produce(rm)


class ExplicitTargetDifficulty(TargetDifficulty):
    """
    A TargetDifficulty that doesn't create StateVectors based on a Robot's possibilities but by choosing from a pool
    of explicitly provided StateVectors
    """

    def __init__(self, stv_pool: List[StateVector], reward_factory: CollectibleFactory, ordered: bool = False):
        """

        :param stv_pool: list of StateVectors to choose from
        :param reward_factory: factory for creating a reward
        :param ordered: whether StateVectors should be chosen in order or randomly from the given stv_pool
        """
        super().__init__(-1, reward_factory)
        self.__pool = stv_pool
        self.__ordered = ordered
        self.__order_index = -1

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        if self.__ordered or rm is None:
            self.__order_index += 1
            if self.__order_index >= len(self.__pool):
                self.__order_index = 0
            stv = self.__pool[self.__order_index]
        else:
            stv = rm.get_element(self.__pool, msg="ExplicitTargetDiff_selectStv")

        if stv.num_of_qubits != robot.num_of_qubits:
            Logger.instance().error(f"Stv (={stv}) from pool does not have correct number of qubits (="
                                    f"{robot.num_of_qubits})!", show=False, from_pycui=False)
        return stv

    def copy_pool(self) -> List[StateVector]:
        return self.__pool.copy()


class RiddleDifficulty(TargetDifficulty):
    def __init__(self, num_of_instructions: int, reward_pool: List[Collectible], min_attempts: int = 1,
                 max_attempts: int = 10):
        super().__init__(num_of_instructions, reward_pool)
        self.__min_attempts = min_attempts
        self.__max_attempts = max_attempts

    def get_attempts(self, rm: MyRandom) -> int:
        return rm.get_int(self.__min_attempts, self.__max_attempts, msg="RiddleDiff.get_attempts()")


class PuzzleDifficulty:
    @staticmethod
    def __create_stv(pool: List[Instruction], num_gates: int, num_qubits: int, rm: MyRandom, inverse: bool = False) \
            -> StateVector:
        instructions: List[Instruction] = []
        for i in range(num_gates):
            # choose random gates on random qubits and cbits
            qubits = list(range(num_qubits))
            instruction = rm.get_element(pool, remove=True, msg="PuzzleDiff_selectInstruction")
            while instruction.use_qubit(rm.get_element(qubits, remove=True, msg="PuzzleDiff_selectQubit")):
                pass
            instructions.append(instruction)
        return Instruction.compute_stv(instructions, num_qubits, inverse)

    def __init__(self, num_input_gates: int, num_target_gates: int):
        self.__num_input_gates = num_input_gates
        self.__num_target_gates = num_target_gates

    def produce(self, robot: Robot, rm: MyRandom) -> Tuple[StateVector, StateVector]:
        instruction_pool = robot.get_available_instructions()
        max_num_gates = min(robot.circuit_space, len(instruction_pool))
        if self.__num_input_gates + self.__num_target_gates > max_num_gates:
            num_input_gates = max(1, max_num_gates - self.__num_target_gates)
            # in case num_target_gates itself is bigger than max_num_gates we have to update it too
            num_target_gates = max_num_gates - num_input_gates
        else:
            num_input_gates, num_target_gates = self.__num_input_gates, self.__num_target_gates

        # input has to be inversed since the player can only apply the corresponding gates from the right of input_stv
        input_stv = PuzzleDifficulty.__create_stv(instruction_pool, min(num_input_gates, robot.circuit_space),
                                                  robot.num_of_qubits, rm, inverse=True)

        # check if we have to re-roll (i.e., input and target are the same)
        remaining_rerolls = 10
        target_stv = PuzzleDifficulty.__create_stv(instruction_pool.copy(), min(num_target_gates, robot.circuit_space),
                                                   robot.num_of_qubits, rm)
        while input_stv.get_diff(target_stv).is_zero and remaining_rerolls > 0:
            target_stv = PuzzleDifficulty.__create_stv(instruction_pool.copy(),
                                                       min(num_target_gates, robot.circuit_space),
                                                       robot.num_of_qubits, rm)
            remaining_rerolls -= 1

        # if remaining_rerolls > 0 we know that the loop above terminated because the vectors are not the same -> done
        if remaining_rerolls <= 0 and input_stv.get_diff(target_stv).is_zero:
            inst_text = "; ".join([str(inst) for inst in robot.get_available_instructions()])
            Logger.instance().warn(f"Couldn't re-roll input and target to be different! {inst_text}", from_pycui=False)
        return input_stv, target_stv


class BossDifficulty:
    @staticmethod
    def from_percentages(num_of_qubits: int, circuit_space: int, circuit_exuberance: float, qubit_exuberance: float,
                         rotation_exuberance: float, randomization_degree: int) -> "BossDifficulty":
        """

        :param num_of_qubits: number of qubits available
        :param circuit_space: maximum number of gates that can be placed in the circuit
        :param circuit_exuberance: how full (]0, 1]) the circuit should be, e.g., 0.5 = half of the circuit_space is
            used, while 1.0 implies all of it is used (if possible based on gates actually available to create the
            puzzle)
        :param qubit_exuberance: how many of the qubits  (]0, 1]) should be rotated randomly, e.g., 0.5 rotates half of
            all qubits, while 1.0 rotates all of them once
        :param rotation_exuberance: how many rotated qubits ([0, 1]) should be rotated along a second axis
        :param randomization_degree: how many angles are available to random rotations (2*PI / randomization_degree),
            a value of 0 implies no restrictions (i.e., any real number is allowed)
        """
        assert 0 < circuit_exuberance <= 1.0, f"Invalid circuit exuberance: 0 < {circuit_exuberance} <= 1 is False!"
        assert 0 < qubit_exuberance <= 1.0, f"Invalid qubit exuberance: 0 < {qubit_exuberance} <= 1 is False!"
        assert 0 <= rotation_exuberance <= 1.0, f"Invalid rotation exuberance: 0 < {rotation_exuberance} <= 1 is False!"

        num_of_gates = int(circuit_space * circuit_exuberance)
        num_of_rotated_qubits = int(num_of_qubits * qubit_exuberance)
        rotation_degree = int(num_of_rotated_qubits * rotation_exuberance)
        return BossDifficulty(num_of_gates, num_of_rotated_qubits, rotation_degree, randomization_degree)

    def __init__(self, num_of_gates: int, num_of_rotated_qubits: int, rotation_degree: int, randomization_degree: int):
        """
        :param randomization_degree: how many angles are available to random rotations (2*PI / randomization_degree),
            a value of 0 implies no restrictions (i.e., any real number is allowed)
        """
        assert num_of_gates > 0, f"At least one gate needs to be placed: {num_of_gates} > 0 is False!"
        assert num_of_rotated_qubits >= 0, f"No negative value allowed for " \
                                           f"num_of_rotated_qubits={num_of_rotated_qubits}"
        assert rotation_degree >= 0, f"No negative value allowed for rotation_degree={rotation_degree}"
        assert randomization_degree >= 0, f"No negative value allowed for randomization_degree={randomization_degree}"

        if rotation_degree > num_of_rotated_qubits:
            Logger.instance().warn(f"rotation_degree (={rotation_degree}) > num_of_rotated_qubits "
                                   f"(={num_of_rotated_qubits}) - using num_of_rotated_qubits instead")
            rotation_degree = num_of_rotated_qubits     # we cannot have more additional rotations than qubits

        self.__num_of_gates = num_of_gates
        self.__num_of_rotated_qubits = num_of_rotated_qubits
        self.__rotation_degree = rotation_degree
        self.__randomization_degree = randomization_degree

    @property
    def num_of_gates(self) -> int:
        """
        :return: how many gates can be used to calculate the target
        """
        return self.__num_of_gates

    @property
    def num_of_rotated_qubits(self) -> int:
        """
        :return: how many qubits should be randomly rotated to determine |In>
        """
        return self.__num_of_rotated_qubits

    @property
    def rotation_degree(self) -> int:
        """
        <= num_of_rotated_qubits
        :return: how many rotated qubits should also be rotated along a second axis
        """
        return self.__rotation_degree

    @property
    def randomization_degree(self) -> int:
        """
        A value of 0 implies no restriction (i.e., any real value is allowed)

        :return: how many degrees of freedom the random rotation angles have
        """
        return self.__randomization_degree

    def normalize(self, num_of_qubits: int, circuit_space: int) -> "BossDifficulty":
        num_of_gates = circuit_space if circuit_space < self.__num_of_gates else self.__num_of_gates
        num_of_rotated_qubits = num_of_qubits if num_of_qubits < self.__num_of_rotated_qubits\
            else self.__num_of_rotated_qubits
        return BossDifficulty(num_of_gates, num_of_rotated_qubits, self.__rotation_degree, self.__randomization_degree)
