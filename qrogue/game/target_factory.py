from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Dict, Union, Tuple

import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.logic import PuzzleGenerator
from qrogue.game.logic.actors import Challenge
from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.actors.puzzles import Enemy, Target, Boss
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, QuantumFuser
from qrogue.game.target_difficulty import ExplicitTargetDifficulty
from qrogue.util import Logger, MyRandom, Config, StvDifficulty, DifficultyType


class EnemyFactory(ABC):
    @staticmethod
    def _fallback_enemy(id_: Optional[int], eid: Optional[int], num_of_qubits: Optional[int],
                        reward: Optional[Collectible], input_stv: Optional[StateVector] = None) -> Enemy:
        if id_ is None: id_ = -1
        if eid is None: eid = 0
        if num_of_qubits is None: num_of_qubits = 2
        return Enemy(id_, eid, StateVector.create_zero_state_vector(num_of_qubits), reward, input_stv)

    @abstractmethod
    def robot_based(self) -> bool:
        pass

    @abstractmethod
    def produce_enemy(self, rm: MyRandom, eid: int,
                      data: Union[Robot, Tuple[Optional[List[Instruction]], Optional[List[Instruction]]]]) -> Enemy:
        pass


class EnemyTargetFactory(EnemyFactory):
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, target_difficulty: ExplicitTargetDifficulty,
                 input_difficulty: Optional[ExplicitTargetDifficulty] = None,
                 next_id_callback: Optional[Callable[[], int]] = None):
        """

        :param target_difficulty: difficulty of the enemy target we produce
        :param input_difficulty: difficulty of the input we produce
        """
        super().__init__()
        if next_id_callback is None:
            self.__next_id = 0

            def _next_id() -> int:
                val = self.__next_id
                self.__next_id += 1
                return val

            self._next_id = _next_id
        else:
            self._next_id = next_id_callback
        self.__target_difficulty = target_difficulty
        self.__input_difficulty = input_difficulty
        self.__custom_reward_factory = None

    def robot_based(self) -> bool:
        return True

    def set_custom_reward_factory(self, factory: CollectibleFactory):
        self.__custom_reward_factory = factory

    def produce_enemy(self, rm: MyRandom, eid: int,
                      data: Union[Robot, Tuple[Optional[List[Instruction]], Optional[List[Instruction]]]]) -> Enemy:
        """
        Creates an enemy based on the number of qubits the provided robot has.

        :param rm:
        :param eid: id in [0, 9] to calculate certain properties
        :param data: Robot
        :return: a freshly created enemy
        """
        if self.__custom_reward_factory:
            reward = self.__custom_reward_factory.produce(rm)
        elif self.__target_difficulty.has_reward_factory:
            reward = self.__target_difficulty.produce_reward(rm)
        else:
            reward = None

        if isinstance(data, Robot):
            robot: Robot = data
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
                        inst_text = "; ".join([str(inst) for inst in robot.instructions])
                        Logger.instance().warn(f"Couldn't re-roll input and target to be different! {inst_text}",
                                               from_pycui=False)
            return Enemy(self._next_id(), eid, target_stv, reward, input_=input_stv)

        Config.check_reachability("EnemyTargetFactory.produce_enemy(Tuple)")
        Logger.instance().error(f"Invalid parameter data! Expected Robot but got \"{type(data)}\"")
        return EnemyFactory._fallback_enemy(self._next_id(), eid, None, reward)


class PuzzleFactory(ABC):
    def __init__(self, difficulty: StvDifficulty, num_of_qubits: int, circuit_space: int,
                 get_available_gates_callback: Callable[[], List[Instruction]],
                 next_id_callback: Optional[Callable[[], int]] = None):
        self.__difficulty = difficulty
        self.__num_of_qubits = num_of_qubits
        self.__circuit_space = circuit_space
        self.__get_available_gates = get_available_gates_callback
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

    @property
    def _difficulty(self) -> StvDifficulty:
        return self.__difficulty

    @property
    def _num_of_qubits(self) -> int:
        return self.__num_of_qubits

    @property
    def _circuit_space(self) -> int:
        return self.__circuit_space

    def _prepare_from_gates(self, rm: MyRandom, include_gates: List[Instruction], force_num_of_gates: bool,
                            inverse: bool = False) -> List[Instruction]:
        return PuzzleGenerator.prepare_from_gates(rm, self.__num_of_qubits, self.__circuit_space, self.__difficulty,
                                                  self.__get_available_gates(), include_gates, force_num_of_gates,
                                                  inverse)

    @abstractmethod
    def produce(self, rm: MyRandom, include_gates: Optional[List[Instruction]],
                input_gates: Optional[List[Instruction]] = None) -> Target:
        pass


class NewEnemyFactory(PuzzleFactory, EnemyFactory):
    def __init__(self, difficulty: StvDifficulty, num_of_qubits: int, circuit_space,
                 get_available_gates_callback: Callable[[], List[Instruction]],
                 reward_pool: Optional[List[Optional[Collectible]]] = None,
                 next_id_callback: Optional[Callable[[], int]] = None):
        super().__init__(difficulty, num_of_qubits, circuit_space, get_available_gates_callback, next_id_callback)
        self.__reward_pool = reward_pool

    def robot_based(self) -> bool:
        return False

    def produce_enemy(self, rm: MyRandom, eid: int,
                      data: Union[Robot, Tuple[Optional[List[Instruction]], Optional[List[Instruction]]]]) -> Enemy:
        if isinstance(data, Tuple):
            include_gates, input_gates = data
            return self.produce(rm, include_gates, input_gates, eid)

        Config.check_reachability("NewEnemyFactory.produce_enemy(Robot)")
        Logger.instance().error(f"Invalid parameter data! Expected Tuple[List[Instruction], List[Instruction] but got "
                                f"\"{type(data)}\"")
        robot: Robot = data
        return EnemyFactory._fallback_enemy(None, eid, robot.num_of_qubits, None)

    def produce(self, rm: MyRandom, include_gates: Optional[List[Instruction]],
                input_gates: Optional[List[Instruction]] = None, eid: Optional[int] = None) -> Enemy:
        eid = 0 if eid is None else eid

        gate_list = self._prepare_from_gates(rm, include_gates, force_num_of_gates=False)
        target_stv = Instruction.compute_stv(gate_list, self._num_of_qubits)

        reward = None if self.__reward_pool is None \
            else rm.get_element(self.__reward_pool, msg="EnemyFactory.produce()@reward")
        return Enemy(self._next_id(), eid, target_stv, reward)


class ChallengeFactory(PuzzleFactory):
    @staticmethod
    def from_robot(difficulty: StvDifficulty, robot: Robot, next_id_callback: Optional[Callable[[], int]] = None) \
            -> "ChallengeFactory":
        available_gates = robot.get_available_instructions()
        return ChallengeFactory(difficulty, robot.num_of_qubits, robot.circuit_space, available_gates, next_id_callback)

    @staticmethod
    def from_difficulty_code(code: str, robot: Robot) -> "BossFactory":
        difficulty = StvDifficulty.from_difficulty_code(code, robot.num_of_qubits, robot.circuit_space)
        assert difficulty.level >= 0, f"Code \"{code}\" produced invalid level: {difficulty.level} >= 0 is False!"
        return BossFactory.from_robot(difficulty, robot)

    def __init__(self, difficulty: StvDifficulty, num_of_qubits: int, circuit_space: int,
                 available_gates: List[Instruction], next_id_callback: Optional[Callable[[], int]] = None):
        super().__init__(difficulty, num_of_qubits, circuit_space, lambda: available_gates, next_id_callback)

    def produce(self, rm: MyRandom, include_gates: Optional[List[Instruction]],
                input_gates: Optional[List[Instruction]] = None) -> Challenge:
        assert len(include_gates) == 1, "Did not provide exactly 1 gate to include in Challenge!"

        input_gates = self._prepare_from_gates(rm, include_gates, force_num_of_gates=False, inverse=True)
        input_stv = Instruction.compute_stv(input_gates, self._num_of_qubits, inverse=True)
        target_stv = StateVector.create_zero_state_vector(self._num_of_qubits)
        # don't specify reward to use the default one
        return Challenge(self._next_id(), target_stv, len(input_gates), len(input_gates), input_=input_stv)


class BossFactory(PuzzleFactory):
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
        if len(BossFactory.__LEVELED_REWARD_POOLS) != StvDifficulty.num_of_difficulty_levels():
            return False
        for i in range(StvDifficulty.num_of_difficulty_levels()):
            if i + StvDifficulty.min_difficulty_level() not in BossFactory.__LEVELED_REWARD_POOLS:
                return False
        return True

    @staticmethod
    def get_leveled_rewards(level: int) -> List[Collectible]:
        assert StvDifficulty.min_difficulty_level() <= level <= StvDifficulty.max_difficulty_level(), \
            "Invalid reward level: " \
            f"{StvDifficulty.min_difficulty_level()} <= {level} <= {StvDifficulty.max_difficulty_level()} is False!"
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
        super().__init__(difficulty, num_of_qubits, circuit_space, lambda: available_gates, next_id_callback)
        self.__reward_pool = reward_pool

    def produce(self, rm: MyRandom, include_gates: Optional[List[Instruction]],
                input_gates: Optional[List[Instruction]] = None) -> Boss:
        """
        :param rm: used for randomization during the puzzle generation
        :param include_gates: a list of gates that will be included in the puzzle additionally to the available gates
        :param input_gates: a list of additional gates used to compute the input stv (don't have to be available to
                            the solving robot)
        """
        # prepare gates to compute target_stv
        ############################
        gates_for_target = self._prepare_from_gates(rm, include_gates, force_num_of_gates=True)
        ############################

        # prepare input_stv either based on input_gates or difficulty
        ############################
        if input_gates is None:
            # prepare gates used for input_stv based on difficulty
            gates_for_input = PuzzleGenerator.prepare_rotation_gates(rm, self._num_of_qubits, self._circuit_space,
                                                                     self._difficulty)
        else:
            qubit_count = [0] * self._num_of_qubits
            qubits = list(range(self._num_of_qubits))
            # prepare gates used for input_stv based on provided input_gates
            Config.check_reachability("BossFactory.produce() with input_gates")
            gates_for_input: List[Instruction] = []
            # use the provided input gates (copy because otherwise the used gates could be changed from the outside)
            for gate in input_gates.copy():
                if BossFactory.__prepare_gate(rm, self._circuit_space, gate, qubit_count, qubits):
                    gates_for_input.append(gate)
        input_stv = Instruction.compute_stv(gates_for_input, self._num_of_qubits)
        ############################

        # generate target_stv based on selected gates and input
        ############################
        # to make sure that the target can be reached from the randomly or manually generated input state,
        #  gates_for_input is prepended to gates_for_target such that the difference between target and input is solely
        #  the previously generated gates_for_target
        target_stv = Instruction.compute_stv(gates_for_input + gates_for_target, self._num_of_qubits)
        ############################

        # pick a reward
        ############################
        reward = QuantumFuser()     #rm.get_element(self.__reward_pool, msg="BossFactory_reward")
        ############################

        edits = self._difficulty.get_absolute_value(DifficultyType.BonusEditRatio, self._num_of_qubits,
                                                    self._circuit_space)
        return Boss(self._next_id(), target_stv, input_stv, reward, edits)

    @staticmethod
    def __prepare_gate(rm: MyRandom, circuit_space: int, gate: Instruction, qubit_count: List[int], qubits: List[int]) \
            -> bool:
        # todo: qubit_count is redundant if we can only place one gate per column
        #  (implying qubit_count can never be > circuit_space if number of placed gates is <= circuit_space)
        gate_qubits = qubits.copy()
        while len(gate_qubits) > 0:
            qubit = rm.get_element(gate_qubits, remove=True, msg="BossFactory_selectQubit")
            qubit_count[qubit] += 1
            if qubit_count[qubit] >= circuit_space:
                qubits.remove(qubit)
            if not gate.use_qubit(qubit):
                return True
        return False
