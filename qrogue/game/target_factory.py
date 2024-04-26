from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Union, Tuple

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.actors.puzzles import Enemy, Target, Riddle, Boss
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, CXGate, SwapGate, Energy, Score
from qrogue.game.logic.collectibles.instruction import YGate, ZGate
from qrogue.game.world.navigation import Direction
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

        # check if we have to re-roll (i.e., input and target are the same
        max_rerolls = 10
        target_stv = PuzzleDifficulty.__create_stv(instruction_pool.copy(), min(num_target_gates, robot.circuit_space),
                                                   robot.num_of_qubits, rm)
        while input_stv.get_diff(target_stv).is_zero and max_rerolls > 0:
            target_stv = PuzzleDifficulty.__create_stv(instruction_pool.copy(),
                                                       min(num_target_gates, robot.circuit_space),
                                                       robot.num_of_qubits, rm)
            max_rerolls -= 1

        # if max_rerolls > 0 we know that the loop above terminated because the vectors are not the same -> done
        if max_rerolls <= 0 and input_stv.get_diff(target_stv).is_zero:
            inst_text = "; ".join([str(inst) for inst in robot.get_available_instructions()])
            Logger.instance().warn(f"Couldn't re-roll input and target to be different! {inst_text}", from_pycui=False)
        return input_stv, target_stv


class EnemyFactory(ABC):
    def __init__(self, start_fight_callback: Callable[[Robot, Enemy, Direction], None],
                 next_id_callback: Optional[Callable[[], int]] = None):
        self.__start_fight = start_fight_callback

        if next_id_callback is None:
            self.__next_id = 0

            def _next_id() -> int:
                val = self.__next_id
                self.__next_id += 1
                return val
            self._next_id = _next_id
        else:
            self._next_id = next_id_callback

    @abstractmethod
    def produce(self, robot: Robot, rm: MyRandom, eid: int) -> Enemy:
        pass

    def start(self, robot: Robot, enemy: Enemy, direction: Direction):
        self.__start_fight(robot, enemy, direction)


class EnemyTargetFactory(EnemyFactory):
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, start_fight_callback: Callable[[Robot, Enemy, Direction], None],
                 target_difficulty: TargetDifficulty, default_flee_chance: float = 0.5,
                 input_difficulty: Optional[StvDifficulty] = None,
                 next_id_callback: Optional[Callable[[], int]] = None):
        """

        :param target_difficulty: difficulty of the enemy target we produce
        :param input_difficulty: difficulty of the input we produce
        """
        super(EnemyTargetFactory, self).__init__(start_fight_callback, next_id_callback)
        self.__target_difficulty = target_difficulty
        self.__default_flee_chance = default_flee_chance
        self.__input_difficulty = input_difficulty
        self.__custom_reward_factory = None

    def set_custom_reward_factory(self, factory: CollectibleFactory):
        self.__custom_reward_factory = factory

    def produce(self, robot: Robot, rm: MyRandom, eid: int) -> Enemy:
        """
        Creates an enemy based on the number of qubits the provided robot has.

        :param robot:
        :param rm:
        :param eid: id in [0, 9] to calculate certain properties
        :return: a freshly created enemy
        """
        if self.__custom_reward_factory:
            reward = self.__custom_reward_factory.produce(rm)
        else:
            reward = self.__target_difficulty.produce_reward(rm)

        target_stv = self.__target_difficulty.create_statevector(robot, rm)
        if self.__input_difficulty is None: input_stv = None
        else:
            max_rerolls = 10
            input_stv = self.__input_difficulty.create_statevector(robot, rm)

            while input_stv.get_diff(target_stv).is_zero and max_rerolls > 0:
                input_stv = self.__input_difficulty.create_statevector(robot, rm)
                max_rerolls -= 1

            # if max_rerolls > 0 we know that the loop above terminated because the vectors are not the same -> done
            if max_rerolls <= 0 and input_stv.get_diff(target_stv).is_zero:
                # try re-rolling the target
                max_rerolls = 10
                target_stv = self.__target_difficulty.create_statevector(robot, rm)
                while input_stv.get_diff(target_stv).is_zero and max_rerolls > 0:
                    target_stv = self.__target_difficulty.create_statevector(robot, rm)
                    max_rerolls -= 1

                if max_rerolls <= 0 and input_stv.get_diff(target_stv).is_zero:
                    inst_text = "; ".join([str(inst) for inst in robot.get_available_instructions()])
                    Logger.instance().warn(f"Couldn't re-roll input and target to be different! {inst_text}",
                                           from_pycui=False)

        return Enemy(self._next_id(), eid, target_stv, reward, input_=input_stv)


class ExplicitEnemyFactory(EnemyTargetFactory):
    def __init__(self, start_fight_callback: Callable[[Robot, Target, Direction], None], stv_pool: List[StateVector],
                 reward_pool: List[Collectible]):
        self.__stv_pool = stv_pool
        self.__reward_pool = reward_pool
        super().__init__(start_fight_callback, TargetDifficulty.dummy())

    def produce(self, robot: Robot, rm: MyRandom, eid: int) -> Enemy:
        stv = rm.get_element(self.__stv_pool, msg="ExplicitEnemyFactory_stv")
        reward = rm.get_element(self.__reward_pool, msg="ExplicitEnemyFactory_reward")
        return Enemy(self._next_id(), eid, stv, reward)


class EnemyPuzzleFactory(EnemyFactory):
    def __init__(self, start_fight_callback: Callable[[Robot, Enemy, Direction], None],
                 next_id_callback: Optional[Callable[[], int]], difficulty: PuzzleDifficulty):
        super().__init__(start_fight_callback, next_id_callback)
        self.__difficulty = difficulty

    def produce(self, robot: Robot, rm: MyRandom, eid: int) -> Enemy:
        input_stv, target_stv = self.__difficulty.produce(robot, rm)
        reward = Score(100)
        return Enemy(self._next_id(), eid, target_stv, reward, input_=input_stv)


class RiddleFactory:
    @staticmethod
    def default(robot: Robot) -> "RiddleFactory":
        reward_pool = [YGate(), ZGate()]
        difficulty = RiddleDifficulty(num_of_instructions=4, reward_pool=reward_pool, min_attempts=4, max_attempts=9)
        return RiddleFactory(robot, difficulty)

    def __init__(self, robot: Robot, difficulty: RiddleDifficulty,
                 next_id_callback: Optional[Callable[[], int]] = None):
        self.__robot = robot
        self.__difficulty = difficulty
        self.__next_id = 0

        if next_id_callback is None:
            self.__next_id = 0

            def _next_id() -> int:
                val = self.__next_id
                self.__next_id += 1
                return val
            self._next_id = _next_id
        else:
            self._next_id = next_id_callback

    def produce(self, rm: MyRandom) -> Riddle:
        stv = self.__difficulty.create_statevector(self.__robot, rm)
        reward = self.__difficulty.produce_reward(rm)
        attempts = self.__difficulty.get_attempts(rm)
        return Riddle(self._next_id(), stv, reward, rm.get_seed("producing a Riddle"), attempts)


class BossFactory:
    @staticmethod
    def default(robot: Robot) -> "BossFactory":
        pool = [CXGate(), SwapGate(), Energy(100)]
        return BossFactory(robot, pool)

    def __init__(self, robot: Robot, reward_pool: List[Collectible],
                 next_id_callback: Optional[Callable[[], int]] = None):
        self.__robot = robot
        self.__reward_pool = reward_pool
        self.__next_id = 0

        if next_id_callback is None:
            self.__next_id = 0

            def _next_id() -> int:
                val = self.__next_id
                self.__next_id += 1
                return val
            self._next_id = _next_id
        else:
            self._next_id = next_id_callback

    def produce(self, rm: MyRandom, include_gates: Optional[List[Instruction]],
                input_gates: Optional[List[Instruction]] = None) -> Boss:
        if include_gates is None: include_gates = []
        if input_gates is None: input_gates = []

        gates_for_target: List[Instruction] = []
        gates_for_input: List[Instruction] = []
        qubit_count = [0] * self.__robot.num_of_qubits
        qubits = list(range(self.__robot.num_of_qubits))

        for g in input_gates:
            # stop before we're using more gates than the robot can place
            if len(gates_for_target) >= self.__robot.circuit_space: break

            gate = g.copy()
            if self.__prepare_gate(rm, gate, qubit_count, qubits): gates_for_input.append(gate)

        for g in include_gates:
            # stop before we're using more gates than the robot can place
            if len(gates_for_target) >= self.__robot.circuit_space: break

            gate = g.copy()
            if self.__prepare_gate(rm, gate, qubit_count, qubits): gates_for_target.append(gate)

        usable_gates = self.__robot.get_available_instructions()
        while len(usable_gates) > 0 and len(gates_for_target) < self.__robot.circuit_space:
            gate = rm.get_element(usable_gates, remove=True, msg="BossFactory_selectGate")
            if self.__prepare_gate(rm, gate, qubit_count, qubits):
                gates_for_target.append(gate)

        reward = rm.get_element(self.__reward_pool, msg="BossFactory_reward")
        return Boss(self._next_id(), [(Instruction.compute_stv(gates_for_target, self.__robot.num_of_qubits),
                                      Instruction.compute_stv(gates_for_input, self.__robot.num_of_qubits))], reward)

    def __prepare_gate(self, rm: MyRandom, gate: Instruction, qubit_count: List[int], qubits: List[int]) -> bool:
        gate_qubits = qubits.copy()
        while len(gate_qubits) > 0:
            qubit = rm.get_element(gate_qubits, remove=True, msg="BossFactory_selectQubit")
            qubit_count[qubit] += 1
            if qubit_count[qubit] >= self.__robot.circuit_space:
                qubits.remove(qubit)
            if not gate.use_qubit(qubit):
                return True
        return False
