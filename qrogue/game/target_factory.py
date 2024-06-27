import math
from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Dict

from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.actors.puzzles import Enemy, Target, Riddle, Boss
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, Energy, Score
import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.target_difficulty import PuzzleDifficulty, ExplicitTargetDifficulty
from qrogue.game.world.navigation import Direction
from qrogue.util import Logger, MyRandom, Config, StvDifficulty, DifficultyType


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
                 target_difficulty: ExplicitTargetDifficulty, default_flee_chance: float = 0.5,
                 input_difficulty: Optional[ExplicitTargetDifficulty] = None,
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
        elif self.__target_difficulty.has_reward_factory:
            reward = self.__target_difficulty.produce_reward(rm)

        target_stv = self.__target_difficulty.create_statevector(robot, rm)
        if self.__input_difficulty is None:
            input_stv = None
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


class EnemyPuzzleFactory(EnemyFactory):
    def __init__(self, start_fight_callback: Callable[[Robot, Enemy, Direction], None],
                 next_id_callback: Optional[Callable[[], int]], difficulty: PuzzleDifficulty):
        super().__init__(start_fight_callback, next_id_callback)
        self.__difficulty = difficulty

    def produce(self, robot: Robot, rm: MyRandom, eid: int) -> Enemy:
        input_stv, target_stv = self.__difficulty.produce(robot, rm)
        reward = Score(100)
        return Enemy(self._next_id(), eid, target_stv, reward, input_=input_stv)


class BossFactory:
    __LEVELED_REWARD_POOLS: Dict[int, List[Collectible]] = {
        0: [gates.XGate(), gates.CXGate(), gates.HGate()],
        1: [gates.HGate(), gates.CXGate(), gates.SwapGate()],
        2: [gates.HGate(), gates.SGate()],
        3: [gates.SGate(), gates.YGate(), gates.ZGate()],
        4: [gates.RYGate(), gates.RZGate()],
        5: [gates.HGate()],
    }

    @staticmethod
    def validate() -> bool:
        if len(BossFactory.__LEVELED_REWARD_POOLS) != StvDifficulty.max_difficulty_level():
            return False
        for i in range(StvDifficulty.max_difficulty_level()):
            if i not in BossFactory.__LEVELED_REWARD_POOLS:
                return False
        return True

    @staticmethod
    def get_leveled_rewards(level: int) -> List[Collectible]:
        assert 0 <= level < StvDifficulty.max_difficulty_level(), \
            f"Invalid reward level: 0 <= {level} < {StvDifficulty.max_difficulty_level()} is False!"
        return BossFactory.__LEVELED_REWARD_POOLS[level].copy()

    @staticmethod
    def from_robot(difficulty: StvDifficulty, robot: Robot, reward_pool: Optional[List[Collectible]] = None,
                   next_id_callback: Optional[Callable[[], int]] = None) -> "BossFactory":
        available_gates = robot.get_available_instructions()
        if reward_pool is None:
            reward_pool = BossFactory.__LEVELED_REWARD_POOLS[difficulty.level]
        return BossFactory(difficulty, robot.num_of_qubits, robot.circuit_space, available_gates, reward_pool,
                           next_id_callback)

    @staticmethod
    def from_difficulty_code(code: str, robot: Robot, reward_pool: Optional[List[Collectible]] = None) -> "BossFactory":
        difficulty = StvDifficulty.from_difficulty_code(code, robot.num_of_qubits, robot.circuit_space)
        assert difficulty.level >= 0, f"Code \"{code}\" produced invalid level: {difficulty.level} >= 0 is False!"
        return BossFactory.from_robot(difficulty, robot, reward_pool)

    @staticmethod
    def from_difficulty_level(level: int, robot: Robot, reward_pool: Optional[List[Collectible]] = None) \
            -> "BossFactory":
        difficulty = StvDifficulty.from_difficulty_level(level, robot.num_of_qubits, robot.circuit_space)
        return BossFactory.from_robot(difficulty, robot, reward_pool)

    @staticmethod
    def default(robot: Robot) -> "BossFactory":
        return BossFactory.from_difficulty_level(1, robot)

    def __init__(self, difficulty: StvDifficulty, num_of_qubits: int, circuit_space: int,
                 available_gates: List[Instruction], reward_pool: List[Collectible],
                 next_id_callback: Optional[Callable[[], int]] = None):
        self.__difficulty = difficulty
        self.__num_of_qubits = num_of_qubits
        self.__circuit_space = circuit_space
        self.__available_gates = available_gates
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
        """
        :param rm: used for randomization during the puzzle generation
        :param include_gates: a list of gates that will be included in the puzzle additionally to the available gates
        :param input_gates: a list of additional gates used to compute the input stv
        """
        if include_gates is None: include_gates = []

        gates_for_target: List[Instruction] = []
        qubit_count = [0] * self.__num_of_qubits
        qubits = list(range(self.__num_of_qubits))

        # absolute difficulty values
        diff_values = self.__difficulty.get_absolute_dict(self.__num_of_qubits, self.__circuit_space)
        num_of_gates = diff_values[DifficultyType.CircuitExuberance]
        num_of_rotated_qubits = diff_values[DifficultyType.QubitExuberance]
        rotation_degree = diff_values[DifficultyType.RotationExuberance]
        randomization_degree = diff_values[DifficultyType.RandomizationDegree]
        edits = diff_values[DifficultyType.BonusEditRatio]

        for g in include_gates:
            # stop before we're using more gates than the robot can place
            if len(gates_for_target) >= self.__circuit_space: break

            gate = g.copy()
            if self.__prepare_gate(rm, gate, qubit_count, qubits): gates_for_target.append(gate)

        usable_gates = self.__available_gates.copy()
        while len(usable_gates) > 0 and len(gates_for_target) < num_of_gates:
            gate = rm.get_element(usable_gates, remove=True, msg="BossFactory_selectGate")
            if self.__prepare_gate(rm, gate, qubit_count, qubits):
                gates_for_target.append(gate)
        rm.shuffle_list(gates_for_target)   # shuffle list so the gates from include_gates don't gather up-front

        gates_for_input: List[Instruction] = []
        if input_gates is None:
            # apply randomly rotated gates to the 0-basis state based on difficulty
            temp_qubit_count = [0] * self.__num_of_qubits
            temp_qubits = qubits.copy()
            rotated_qubits = [rm.get_element(temp_qubits, remove=True) for _ in range(num_of_rotated_qubits)]
            rotated_qubits2 = rotated_qubits.copy()

            for _ in range(len(rotated_qubits) - rotation_degree):
                # remove qubits until only #rotation_degree qubits are left in rotated_qubits2
                rm.get_element(rotated_qubits2, remove=True)

            for qubit in rotated_qubits:
                # find a random angle for the rotation
                if randomization_degree == 0:
                    angle = rm.get(msg="BossFactory.produce()_unrestrictedAngle")
                else:   # todo: what about randomization_degree==1?
                    # start with 1 because rotating by 0° does nothing (since range-end is exclusive, 360° can't happen)
                    angle = rm.get_element([(2*math.pi) * i / randomization_degree
                                            for i in range(1, randomization_degree)],
                                           msg="BossFactory.produce()_restrictedAngle")
                # prepare and append either an RY- or RZGate
                rotate_y = rm.get_bool(msg="BossFactory.produce()_chooseRGate")
                gate = gates.RYGate(angle) if rotate_y else gates.RZGate(angle)
                self.__prepare_gate(rm, gate, temp_qubit_count, [qubit])
                gates_for_input.append(gate)
                # append the other rotational gate if the qubit is also in rotated_qubits2
                if qubit in rotated_qubits2:
                    # now use RZGate if rotate_y is True (RYGate was used before), and vice versa
                    gate = gates.RZGate(angle) if rotate_y else gates.RYGate(angle)
                    self.__prepare_gate(rm, gate, temp_qubit_count, [qubit])
                    gates_for_input.append(gate)

            # to make sure that the target can be reached from the randomized input state, gates_for_input is prepended
            #  to gates_for_target such that the difference between target and input is solely the previously generated
            #  gates_for_target
            gates_for_target = gates_for_input + gates_for_target

        else:
            Config.check_reachability("BossFactory.produce() with input_gates")
            # use the provided input gates
            for g in input_gates:
                # stop before we're using more gates than the robot can place
                if len(gates_for_target) >= self.__circuit_space: break

                gate = g.copy()
                if self.__prepare_gate(rm, gate, qubit_count, qubits): gates_for_input.append(gate)

        target_stv = Instruction.compute_stv(gates_for_target, self.__num_of_qubits)
        input_stv = Instruction.compute_stv(gates_for_input, self.__num_of_qubits)
        reward = rm.get_element(self.__reward_pool, msg="BossFactory_reward")
        return Boss(self._next_id(), target_stv, input_stv, reward, edits)

    def __prepare_gate(self, rm: MyRandom, gate: Instruction, qubit_count: List[int], qubits: List[int]) -> bool:
        gate_qubits = qubits.copy()
        while len(gate_qubits) > 0:
            qubit = rm.get_element(gate_qubits, remove=True, msg="BossFactory_selectQubit")
            qubit_count[qubit] += 1
            if qubit_count[qubit] >= self.__circuit_space:
                qubits.remove(qubit)
            if not gate.use_qubit(qubit):
                return True
        return False
