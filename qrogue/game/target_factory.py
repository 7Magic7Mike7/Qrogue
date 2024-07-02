import math
from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Dict, Tuple, Set

from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.actors.puzzles import Enemy, Target, Riddle, Boss
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction, Energy, Score
import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.target_difficulty import PuzzleDifficulty, ExplicitTargetDifficulty
from qrogue.game.world.navigation import Direction
from qrogue.util import Logger, MyRandom, Config, StvDifficulty, DifficultyType, RandomManager


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
        :param input_gates: a list of additional gates used to compute the input stv (don't have to be available to
                            the solving robot)
        """
        # prepare gates to compute target_stv
        ############################
        gates_for_target = BossFactory.prepare_target(rm, self.__num_of_qubits, self.__circuit_space, self.__difficulty,
                                                      self.__available_gates, include_gates)
        ############################

        # prepare input_stv either based on input_gates or difficulty
        ############################
        if input_gates is None:
            # prepare gates used for input_stv based on difficulty
            gates_for_input = BossFactory.prepare_input(rm, self.__num_of_qubits, self.__circuit_space,
                                                        self.__difficulty)
        else:
            qubit_count = [0] * self.__num_of_qubits
            qubits = list(range(self.__num_of_qubits))
            # prepare gates used for input_stv based on provided input_gates
            Config.check_reachability("BossFactory.produce() with input_gates")
            gates_for_input: List[Instruction] = []
            # use the provided input gates (copy because otherwise the used gates could be changed from the outside)
            for gate in input_gates.copy():
                if BossFactory.__prepare_gate(rm, self.__circuit_space, gate, qubit_count, qubits):
                    gates_for_input.append(gate)
        input_stv = Instruction.compute_stv(gates_for_input, self.__num_of_qubits)
        ############################

        # generate target_stv based on selected gates and input
        ############################
        # to make sure that the target can be reached from the randomly or manually generated input state,
        #  gates_for_input is prepended to gates_for_target such that the difference between target and input is solely
        #  the previously generated gates_for_target
        target_stv = Instruction.compute_stv(gates_for_input + gates_for_target, self.__num_of_qubits)
        ############################

        # pick a reward
        ############################
        reward = rm.get_element(self.__reward_pool, msg="BossFactory_reward")
        ############################

        edits = self.__difficulty.get_absolute_value(DifficultyType.BonusEditRatio, self.__num_of_qubits,
                                                     self.__circuit_space)
        return Boss(self._next_id(), target_stv, input_stv, reward, edits)

    @staticmethod
    def __prepare_gate(rm: MyRandom, circuit_space: int, gate: Instruction, qubit_count: List[int], qubits: List[int]) -> bool:
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

    @staticmethod
    def __prepare_gate_at(rm: MyRandom, circuit_space: int, gate: Instruction, qubit_count: List[int],
                          qubits: List[int], qubit: int) -> bool:
        gate_qubits = qubits.copy()
        assert qubit in gate_qubits, f"Invalid arguments: qubit={qubit} not in qubits={qubits}!"
        gate_qubits.remove(qubit)

        qubit_count[qubit] += 1
        if qubit_count[qubit] >= circuit_space:
            qubits.remove(qubit)

        if gate.use_qubit(qubit):
            # don't remove here because removal happens in the next recursion step (because we need to pass a qubit
            #  that is still in qubits for the very first call)
            next_qubit = rm.get_element(gate_qubits, remove=False, msg="BossFactory_selectQubit")
            return BossFactory.__prepare_gate_at(rm, circuit_space, gate, qubit_count, gate_qubits, next_qubit)
        return True

    @staticmethod
    def get_angle(rm: MyRandom, randomization_degree: int) -> float:
        if randomization_degree == 0:
            angle = rm.get(msg="BossFactory.produce()_unrestrictedAngle")
        else:  # todo: what about randomization_degree==1?
            # start with 1 because rotating by 0° does nothing (since range-end is exclusive, 360° can't happen)
            angle = rm.get_element([(2 * math.pi) * i / randomization_degree
                                    for i in range(1, randomization_degree)],
                                   msg="BossFactory.produce()_restrictedAngle")
        return angle

    @staticmethod
    def prepare_input(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty) \
            -> List[Instruction]:
        input_gates: List[Instruction] = []

        # 1) retrieve variables
        ############################
        diff_values = difficulty.get_absolute_dict(num_of_qubits, circuit_space)
        num_of_rotated_qubits = diff_values[DifficultyType.QubitExuberance]
        rotation_degree = diff_values[DifficultyType.RotationExuberance]
        randomization_degree = diff_values[DifficultyType.RandomizationDegree]
        ############################

        # 2) decide which qubits should receive rotations
        ############################
        qubit_count = [0] * num_of_qubits
        qubits = list(range(num_of_qubits))

        # get random qubits to fill the rotated_qubits list
        rotated_qubits = [rm.get_element(qubits, remove=True) for _ in range(num_of_rotated_qubits)]

        if rotation_degree > 0:
            rotated_qubits2 = rotated_qubits.copy()
            # randomly remove qubits until only #rotation_degree qubits are left in rotated_qubits2
            for _ in range(len(rotated_qubits) - rotation_degree):
                rm.get_element(rotated_qubits2, remove=True)
        else:
            # no qubit receives a second rotation
            rotated_qubits2 = []
        ############################

        # 3) apply rotation gates to the 0-basis state based on previously selected qubits
        ############################
        for qubit in rotated_qubits:
            # find a random angle for the rotation
            angle = BossFactory.get_angle(rm, randomization_degree)

            # prepare and append either an RY- or RZ-Gate
            rotate_y = rm.get_bool(msg="BossFactory.produce()_chooseRGate")
            rot_gate1 = gates.RYGate(angle) if rotate_y else gates.RZGate(angle)
            BossFactory.__prepare_gate(rm, circuit_space, rot_gate1, qubit_count, [qubit])
            input_gates.append(rot_gate1)

            # append the other rotational gate if the qubit is also in rotated_qubits2 (i.e., it receives two rotations)
            if qubit in rotated_qubits2:
                # now use RZGate if rotate_y is True (RYGate was used before), and vice versa
                rot_gate2 = gates.RZGate(angle) if rotate_y else gates.RYGate(angle)
                BossFactory.__prepare_gate(rm, circuit_space, rot_gate2, qubit_count, [qubit])
                input_gates.append(rot_gate2)
        ############################

        return input_gates

    @staticmethod
    def prepare_target(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty,
                       available_gates: List[Instruction], include_gates: Optional[List[Instruction]],
                       force_num_of_gates: bool = False) -> List[Instruction]:
        available_gates = available_gates.copy()    # copy it because we might remove elements during selection

        # 1) prepare variables
        ##################################
        if include_gates is None: include_gates = []
        num_of_gates = difficulty.get_absolute_value(DifficultyType.CircuitExuberance, num_of_qubits, circuit_space)

        if len(include_gates) > num_of_gates:
            Logger.instance().warn(f"Cannot use all included gates: only {num_of_gates} out of {len(include_gates)} "
                                   f"will be used.", from_pycui=False)
        ##################################

        # 2) select the gates to choose for target
        ##################################
        if len(include_gates) + len(available_gates) <= num_of_gates:
            # we don't have enough gates to be picky, so we choose all we can
            selected_gates = include_gates + available_gates
        else:
            selected_gates = include_gates.copy()   # include_gates need to be used
            while len(selected_gates) < num_of_gates:
                # add random ones from available_gates to the selection
                selected_gates.append(rm.get_element(available_gates, remove=True,
                                                     msg="BossFactory.prepare_target()@gates_for_target"))
        rm.shuffle_list(selected_gates)
        ##################################

        if force_num_of_gates:
            return BossFactory.__prepare_nearsighted_circuit(rm, num_of_qubits, circuit_space, selected_gates)
        else:
            return BossFactory.__prepare_farsighted_circuit(rm, num_of_qubits, circuit_space, selected_gates)

    @staticmethod
    def __prepare_nearsighted_circuit(rm: MyRandom, num_of_qubits: int, circuit_space: int,
                                      selected_gates: List[Instruction]) -> List[Instruction]:
        """
        Prepares a list of gates (representing a circuit) such that any two consecutive gates on a qubit don't cancel
        each other out. It is still possible that, e.g., the gate placed third cancels the combination of the first and
        second gate.
        """
        qubit_count = [0] * num_of_qubits
        qubits = list(range(num_of_qubits))

        # store which stvs we generated on the way to make sure we don't undo a previous gate (leading to virtually
        #  fewer gates used than tasked with) - starting with no gates applied, we're at the 0-state
        prev_stvs: Set[StateVector] = {StateVector.create_zero_state_vector(num_of_qubits)}
        circuits: List[List[gates.Instruction]] = [[]]

        i, start_index = 0, 0
        while True:
            added_gate = False
            cur_qubits = qubits.copy()
            rm.shuffle_list(cur_qubits)
            # try to add the currently selected gate on different qubits until the resulting stv is completely new
            for qu in cur_qubits:
                cur_gate = selected_gates[i].copy()
                BossFactory.__prepare_gate_at(rm, circuit_space, cur_gate, qubit_count, qubits, qu)

                real_circuit = circuits[-1]
                new_stv = gates.Instruction.compute_stv(real_circuit.copy() + [cur_gate], num_of_qubits)

                # check whether new_stv is indeed new or a repeat of a previous one (meaning the gate undid an operation)
                is_repeated = False
                for prev_stv in prev_stvs:
                    if prev_stv.is_equal_to(new_stv, ignore_god_mode=True):
                        is_repeated = True  # we found a duplicate
                        break

                if not is_repeated:
                    # gates_for_target and cur_gate result in a new stv -> save cur_gate to gates_for_target
                    # gates_for_target.append(cur_gate)
                    # prev_stvs.append(new_stv)  # also store the resulting stv for comparison with new ones
                    new_circuits = []
                    for circuit in circuits:
                        new_circuit = circuit.copy() + [cur_gate]
                        new_circuits.append(new_circuit)
                        prev_stvs.add(gates.Instruction.compute_stv(new_circuit, num_of_qubits))
                    circuits += new_circuits

                    added_gate = True
                    break

            # ret_val = BossFactory.__next_gate(i, start_index, added_gate, selected_gates)
            # if ret_val is None: break
            # i, start_index, selected_gates = ret_val
            if added_gate:
                # remove cur_gate (at index i) from selectable gates
                if len(selected_gates) == 1:
                    break  # we just placed the last gate
                elif i + 1 >= len(selected_gates):
                    selected_gates = selected_gates[:i]
                else:
                    selected_gates = selected_gates[:i] + selected_gates[i + 1:]
                # don't increment i since it already points to a new gate
                if i >= len(selected_gates): i = 0  # change i by starting over if it would be out of bounds
                start_index = i  # store where the search for the next gate started, so we can stop before repeating
            else:
                i += 1  # try the next gate
                if i >= len(selected_gates): i = 0
                if i == start_index:
                    Config.check_reachability("target_stv generation unsuccessful")
                    break  # we couldn't add all selected gates

        return circuits[-1]

    @staticmethod
    def __prepare_farsighted_circuit(rm: MyRandom, num_of_qubits: int, circuit_space: int,
                                     selected_gates: List[Instruction]) -> List[Instruction]:
        """
        Prepares a list of gates (representing a circuit) such that gate cancels out any previously placed gates. This
        way it is not ensured that all gates in selected_gates are in the circuit, but adding one of these remaining
        gates to any qubit would result in a circuit that either produces the same StateVector or a StateVector closer
        to the 0-state (i.e., undoing one of the previous gates).
        """
        # todo: a bad gate selection can lead to being unable to place enough gates - fix with additional parameters and
        #  selecting gates on the fly? (but we have to make sure that included_gates are used!)
        # todo: maybe we can
        #  change included_gates to a single gate (ComposedGates would still allow to use multiple)
        qubit_count = [0] * num_of_qubits
        qubits = list(range(num_of_qubits))

        last_gate_dict: Dict[int, Optional[Instruction]] = {}
        for cur_qubit in qubits: last_gate_dict[cur_qubit] = None

        circuit = []
        i, start_index = 0, 0
        while True:
            added_gate = False
            cur_qubits = qubits.copy()
            rm.shuffle_list(cur_qubits)
            # try to add the currently selected gate on different qubits until the resulting stv is completely new
            for cur_qubit in cur_qubits:
                cur_gate = selected_gates[i].copy()
                BossFactory.__prepare_gate_at(rm, circuit_space, cur_gate, qubit_count, qubits, cur_qubit)

                # if stv of circuit together with cur_gate would result in a 0-state, we continue with the next qubit
                if Instruction.compute_stv(circuit + [cur_gate], num_of_qubits).is_zero: continue

                # check if the last gate on cur_qubit is cancelled by cur_gate
                if last_gate_dict[cur_qubit] is not None and \
                        Instruction.compute_stv([last_gate_dict[cur_qubit], cur_gate], num_of_qubits).is_zero:
                    continue

                # circuit and cur_gate result in a new stv -> save cur_gate to circuit
                circuit.append(cur_gate)
                # update last_gate_dict based on newly appended cur_gate
                for qu in cur_gate.qargs_iter(): last_gate_dict[qu] = cur_gate
                # set added_gate flag, so we now that we can remove cur_gate from selected_gates
                added_gate = True
                break

            #ret_val = BossFactory.__next_gate(i, start_index, added_gate, selected_gates)
            #if ret_val is None: break
            #i, start_index, selected_gates = ret_val
            if added_gate:
                # remove cur_gate (at index i) from selectable gates
                if len(selected_gates) == 1:
                    break  # we just placed the last gate
                elif i + 1 >= len(selected_gates):
                    selected_gates = selected_gates[:i]
                else:
                    selected_gates = selected_gates[:i] + selected_gates[i + 1:]
                # don't increment i since it already points to a new gate
                if i >= len(selected_gates): i = 0  # change i by starting over if it would be out of bounds
                start_index = i  # store where the search for the next gate started, so we can stop before repeating
            else:
                i += 1  # try the next gate
                if i >= len(selected_gates): i = 0
                if i == start_index:
                    Config.check_reachability("target_stv generation unsuccessful")
                    break  # we couldn't add all selected gates

        return circuit

    @staticmethod
    def __next_gate(index: int, start_index: int, added_gate: bool, gate_list: List[Instruction]) \
            -> Optional[Tuple[int, int, List[Instruction]]]:    # todo: fix and use
        if added_gate:
            # remove cur_gate (at index i) from selectable gates
            if len(gate_list) == 1:
                return None  # we just placed the last gate
            elif index + 1 >= len(gate_list):
                selected_gates = gate_list[:index]
            else:
                selected_gates = gate_list[:index] + gate_list[index + 1:]
            # don't increment i since it already points to a new gate
            if index >= len(selected_gates): i = 0  # change i by starting over if it would be out of bounds
            start_index = index  # store where the search for the next gate started, so we can stop before repeating
        else:
            index += 1  # try the next gate
            if index >= len(gate_list): index = 0
            if index == start_index:
                Config.check_reachability("target_stv generation unsuccessful")
                return None  # we couldn't add all selected gates

        return index, start_index, gate_list

    @staticmethod
    def generate_puzzle(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty,
                        available_gates: List[Instruction], include_gates: Optional[List[Instruction]],
                        reward_pool: List[Collectible]) -> Tuple[StateVector, StateVector, Optional[Collectible]]:
        irm = RandomManager.create_new(rm.get_seed())   # input rm
        trm = RandomManager.create_new(rm.get_seed())   # target rm
        rrm = RandomManager.create_new(rm.get_seed())   # reward rm

        input_gates = BossFactory.prepare_input(irm, num_of_qubits, circuit_space, difficulty)
        input_stv = Instruction.compute_stv(input_gates, num_of_qubits)

        target_gates = BossFactory.prepare_target(trm, num_of_qubits, circuit_space, difficulty, available_gates,
                                                  include_gates)
        target_stv = Instruction.compute_stv(input_gates + target_gates, num_of_qubits)

        reward = rrm.get_element(reward_pool, msg="generate_puzzle()-reward")

        return input_stv, target_stv, reward
