from abc import abstractmethod, ABC
from typing import List, Callable, Optional

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.actors.puzzles import Enemy, Target, Riddle, Boss
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, Energy, Score
from qrogue.game.logic.collectibles.instruction import CXGate, SwapGate, YGate, ZGate
from qrogue.game.target_difficulty import StvDifficulty, TargetDifficulty, PuzzleDifficulty, RiddleDifficulty
from qrogue.game.world.navigation import Direction
from qrogue.util import Logger, MyRandom


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
