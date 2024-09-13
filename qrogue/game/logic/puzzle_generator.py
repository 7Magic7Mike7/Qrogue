import math
from typing import List, Optional, Tuple, Dict, Set

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, Instruction
from qrogue.game.logic.collectibles.instruction import RZGate, RYGate
from qrogue.util import MyRandom, RandomManager, DifficultyType, StvDifficulty, Config, Logger


class PuzzleGenerator:
    __MAX_TRIES = 5

    @staticmethod
    def __prepare_gate_at(rm: MyRandom, circuit_space: int, gate: Instruction, qubit_count: List[int],
                          qubits: List[int], qubit: int) -> bool:
        """
        :returns: True if gate was successfully prepared, False otherwise
        """
        gate_qubits = qubits.copy()
        assert qubit in gate_qubits, f"Invalid arguments: qubit={qubit} not in qubits={qubits}!"
        gate_qubits.remove(qubit)

        qubit_count[qubit] += 1
        if qubit_count[qubit] >= circuit_space:
            qubits.remove(qubit)

        if gate.use_qubit(qubit):
            if len(qubits) <= 0:
                Logger.instance().error(f"Not enough qubits provided to prepare gate {gate.name()}!", from_pycui=False)
                return False
            # don't remove here because removal happens in the next recursion step (because we need to pass a qubit
            #  that is still in qubits for the very first call)
            next_qubit = rm.get_element(gate_qubits, remove=False, msg="BossFactory_selectQubit")
            return PuzzleGenerator.__prepare_gate_at(rm, circuit_space, gate, qubit_count, gate_qubits, next_qubit)
        return True

    @staticmethod
    def __get_angle(rm: MyRandom, randomization_degree: int) -> float:
        if randomization_degree == 0:
            angle = rm.get(msg="PuzzleGenerator.produce()_unrestrictedAngle")
        else:  # todo: what about randomization_degree==1?
            # start with 1 because rotating by 0° does nothing (since range-end is exclusive, 360° can't happen)
            angle = rm.get_element([(2 * math.pi) * i / randomization_degree
                                    for i in range(1, randomization_degree)],
                                   msg="PuzzleGenerator.produce()_restrictedAngle")
        return angle

    @staticmethod
    def prepare_single_layer_gates(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty,
                                   available_gates: List[Instruction]) -> List[Instruction]:
        """
        Prepares at most one single-qubit gate per qubit.

        :param rm: determines randomness
        :param num_of_qubits: how many qubits can be used to place gates on
        :param circuit_space: the maximum number of gates that can be placed in the circuit
        :param difficulty: determines absolute value of QubitExuberance, and hence, how many gates we try to prepare
                            relative to num_of_qubits
        :param available_gates: the gates available for preparation
        :returns: list of prepared (i.e., ready to compute a StateVector) gates
        """
        gate_list = []
        # 1) extract difficulty value
        num_of_single_layer_qubits = difficulty.get_absolute_value(DifficultyType.QubitExuberance, num_of_qubits,
                                                                   circuit_space)
        # 2) decide on which qubits we apply a single gate
        qubit_count = [0] * num_of_qubits
        qubits = list(range(num_of_qubits))
        single_layer_qubits = [rm.get_element(qubits, remove=True) for _ in range(num_of_single_layer_qubits)]

        # 3) filter for single qubit gates
        filtered_gates = [gate for gate in available_gates if gate.num_of_qubits == 1]

        # 4) apply single qubit gates to the selected qubits
        for qubit in single_layer_qubits:
            if len(filtered_gates) <= 0: break
            gate = rm.get_element(filtered_gates, remove=True)
            if PuzzleGenerator.__prepare_gate_at(rm, circuit_space, gate, qubit_count, [qubit], qubit):
                gate_list.append(gate)

        return gate_list

    @staticmethod
    def prepare_rotation_gates(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty) \
            -> List[Instruction]:
        rotation_gates: List[Instruction] = []

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
            angle = PuzzleGenerator.__get_angle(rm, randomization_degree)

            # prepare and append either an RY- or RZ-Gate
            rotate_y = rm.get_bool(msg="PuzzleGenerator.produce()_chooseRGate")
            rot_gate1 = RYGate(angle) if rotate_y else RZGate(angle)
            if PuzzleGenerator.__prepare_gate_at(rm, circuit_space, rot_gate1, qubit_count, [qubit], qubit):
                rotation_gates.append(rot_gate1)

            # append the other rotational gate if the qubit is also in rotated_qubits2 (i.e., it receives two rotations)
            if qubit in rotated_qubits2:
                # now use RZGate if rotate_y is True (RYGate was used before), and vice versa
                rot_gate2 = RZGate(angle) if rotate_y else RYGate(angle)
                if PuzzleGenerator.__prepare_gate_at(rm, circuit_space, rot_gate2, qubit_count, [qubit], qubit):
                    rotation_gates.append(rot_gate2)
        ############################

        return rotation_gates

    @staticmethod
    def prepare_from_gates(rm: MyRandom, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty,
                           available_gates: List[Instruction], include_gates: Optional[List[Instruction]],
                           force_num_of_gates: bool = False, inverse: bool = False) -> List[Instruction]:
        available_gates = available_gates.copy()  # copy it because we might remove elements during selection

        # 1) prepare variables
        ##################################
        if include_gates is None: include_gates = []
        num_of_gates = difficulty.get_absolute_value(DifficultyType.CircuitExuberance, num_of_qubits, circuit_space)

        if len(include_gates) > num_of_gates:
            Logger.instance().warn(f"Cannot use all included gates: only {num_of_gates} out of {len(include_gates)} "
                                   f"will be used.", from_pycui=False)
        ##################################

        gate_list = []
        prepare_rm = RandomManager.create_new(rm.get_seed("PrepareRM"))
        for _ in range(PuzzleGenerator.__MAX_TRIES):    # try multiple times if we fail to generate a gate_list
            l_available_gates = available_gates.copy()  # copy available_gates since we remove elements later

            # 2) select the gates to choose for target
            ##################################
            if len(include_gates) + len(l_available_gates) <= num_of_gates:
                # we don't have enough gates to be picky, so we choose all we can
                selected_gates = include_gates + l_available_gates
            else:
                selected_gates = include_gates.copy()  # include_gates need to be used
                while len(selected_gates) < num_of_gates:
                    # add random ones from available_gates to the selection
                    selected_gates.append(rm.get_element(l_available_gates, remove=True,
                                                         msg="PuzzleGenerator.prepare_target()@gates_for_target"))
            rm.shuffle_list(selected_gates)
            ##################################

            # 3) prepare gate_list
            ##################################
            if force_num_of_gates:
                gate_list = PuzzleGenerator.__prepare_nearsighted_circuit(prepare_rm, num_of_qubits, circuit_space,
                                                                          selected_gates, inverse)
                # in this case it is fine as long as we prepared at least one gate
                if len(gate_list) > 0: break
            else:
                gate_list = PuzzleGenerator.__prepare_farsighted_circuit(prepare_rm, num_of_qubits, circuit_space,
                                                                         selected_gates, inverse)
                # in this case we need to prepare at least half the expected number of gates
                if len(gate_list) >= len(selected_gates) / 2: break
            ##################################

            # 4) retry if needed
            Config.check_reachability("Retry gate_list generation.")
            prepare_rm = RandomManager.create_new(rm.get_seed("PrepareRM-while"))
        return gate_list

    @staticmethod
    def __prepare_nearsighted_circuit(rm: MyRandom, num_of_qubits: int, circuit_space: int,
                                      selected_gates: List[Instruction], inverse: bool = False) -> List[Instruction]:
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
        circuits: List[List[Instruction]] = [[]]

        i, start_index = 0, 0
        while True:
            added_gate = False
            cur_qubits = qubits.copy()
            rm.shuffle_list(cur_qubits)
            # try to add the currently selected gate on different qubits until the resulting stv is completely new
            for qu in cur_qubits:
                cur_gate = selected_gates[i].copy()
                if not PuzzleGenerator.__prepare_gate_at(rm, circuit_space, cur_gate, qubit_count, qubits, qu):
                    continue    # failed to prepare the gate, so let's try with a different qubit

                real_circuit = circuits[-1]
                new_stv = Instruction.compute_stv(real_circuit.copy() + [cur_gate], num_of_qubits, inverse)

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
                        prev_stvs.add(Instruction.compute_stv(new_circuit, num_of_qubits, inverse))
                    circuits += new_circuits

                    added_gate = True
                    break

            # ret_val = PuzzleGenerator.__next_gate(i, start_index, added_gate, selected_gates)
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
                                     selected_gates: List[Instruction], inverse: bool = False) -> List[Instruction]:
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
                if not PuzzleGenerator.__prepare_gate_at(rm, circuit_space, cur_gate, qubit_count, qubits, cur_qubit):
                    continue    # failed to prepare the gate, so let's try with a different qubit

                # if stv of circuit together with cur_gate would result in a 0-state, we continue with the next qubit
                if Instruction.compute_stv(circuit + [cur_gate], num_of_qubits, inverse).is_zero: continue

                # check if the last gate on cur_qubit is cancelled by cur_gate
                if last_gate_dict[cur_qubit] is not None and \
                        Instruction.compute_stv([last_gate_dict[cur_qubit], cur_gate], num_of_qubits, inverse).is_zero:
                    continue

                # circuit and cur_gate result in a new stv -> save cur_gate to circuit
                circuit.append(cur_gate)
                # update last_gate_dict based on newly appended cur_gate
                for qu in cur_gate.qargs_iter(): last_gate_dict[qu] = cur_gate
                # set added_gate flag, so we now that we can remove cur_gate from selected_gates
                added_gate = True
                break

            # ret_val = PuzzleGenerator.__next_gate(i, start_index, added_gate, selected_gates)
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

        return circuit

    @staticmethod
    def __next_gate(index: int, start_index: int, added_gate: bool, gate_list: List[Instruction]) \
            -> Optional[Tuple[int, int, List[Instruction]]]:  # todo: fix and use
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
        irm = RandomManager.create_new(rm.get_seed())  # input rm
        trm = RandomManager.create_new(rm.get_seed())  # target rm
        rrm = RandomManager.create_new(rm.get_seed())  # reward rm

        input_gates = PuzzleGenerator.prepare_rotation_gates(irm, num_of_qubits, circuit_space, difficulty)
        input_stv = Instruction.compute_stv(input_gates, num_of_qubits)

        target_gates = PuzzleGenerator.prepare_from_gates(trm, num_of_qubits, circuit_space, difficulty,
                                                          available_gates, include_gates)
        target_stv = Instruction.compute_stv(input_gates + target_gates, num_of_qubits)

        reward = rrm.get_element(reward_pool, msg="generate_puzzle()-reward")

        return input_stv, target_stv, reward
