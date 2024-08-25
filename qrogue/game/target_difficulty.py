from typing import List, Union, Tuple, Optional

from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction
from qrogue.util import Logger, MyRandom


class ExplicitTargetDifficulty:
    """
    A TargetDifficulty that doesn't create StateVectors based on a Robot's possibilities but by choosing from a pool
    of explicitly provided StateVectors
    """

    def __init__(self, stv_pool: List[StateVector], reward: Optional[Union[CollectibleFactory, Collectible]] = None,
                 ordered: bool = False):
        """

        :param stv_pool: list of StateVectors to choose from
        :param reward: factory for creating a reward or a specific reward (Collectible)
        :param ordered: whether StateVectors should be chosen in order or randomly from the given stv_pool
        """
        self.__pool = stv_pool
        self.__ordered = ordered
        self.__order_index = -1
        if reward is None:
            self.__reward_factory = None
        elif isinstance(reward, CollectibleFactory):
            self.__reward_factory = reward
        else:
            self.__reward_factory = CollectibleFactory([reward])

    @property
    def has_reward_factory(self) -> bool:
        return self.__reward_factory is not None

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        if self.__ordered or rm is None:
            self.__order_index += 1
            if self.__order_index >= len(self.__pool):
                self.__order_index = 0
            stv = self.__pool[self.__order_index]
        else:
            stv = rm.get_element(self.__pool, msg="ExplicitTargetDiff_selectStv")

        if stv.num_of_qubits != robot.num_of_qubits:
            Logger.instance().warn(f"Stv (={stv}) from pool does not have correct number of qubits (="
                                   f"{robot.num_of_qubits})!", show=False, from_pycui=False)
        return stv

    def produce_reward(self, rm: MyRandom) -> Optional[Collectible]:
        if self.__reward_factory is None:
            return None
        return self.__reward_factory.produce(rm)

    def copy_pool(self) -> List[StateVector]:
        return self.__pool.copy()


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
            inst_text = "; ".join([str(inst) for inst in robot.instructions])
            Logger.instance().warn(f"Couldn't re-roll input and target to be different! {inst_text}", from_pycui=False)
        return input_stv, target_stv
