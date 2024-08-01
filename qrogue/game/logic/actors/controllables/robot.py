"""
Author: Artner Michael
13.06.2021
"""
from abc import ABC
from typing import Tuple, List, Callable, Optional, Iterator, Union

from qrogue.game.logic.actors.controllables import Controllable
from qrogue.game.logic.actors.controllables.qubit import QubitSet, DummyQubitSet
from qrogue.game.logic.base import StateVector, CircuitMatrix, QuantumSimulator, QuantumCircuit, UnitarySimulator
from qrogue.game.logic.collectibles import Collectible, Instruction, Key, MultiCollectible, \
    Qubit, Energy, Score, InstructionManager
from qrogue.util import CheatConfig, Config, Logger, GameplayConfig, QuantumSimulationConfig, Options, GateType


# from jkq import ddsim
class RoboProperties:
    def __init__(self, num_of_qubits: int = 3, circuit_space: int = 5, gate_list: Optional[List[Instruction]] = None):
        self.__num_of_qubits = num_of_qubits
        self.__circuit_space = circuit_space
        self.__gate_list = gate_list

    @property
    def num_of_qubits(self) -> int:
        return self.__num_of_qubits

    @property
    def circuit_space(self) -> int:
        return self.__circuit_space

    @property
    def instruction_list(self) -> Optional[List[Instruction]]:
        if self.__gate_list is None: return None
        return [gate.copy() for gate in self.__gate_list]


class _Attributes:
    """
    A class that handles some attributes of a Robot.
    """
    # todo: Overhaul whole class?
    __DEFAULT_SPACE = 5
    __DEFAULT_MAX_ENERGY = 100
    __MIN_INIT_ENERGY = 1  # during initialization neither max_energy nor cur_energy must be below this value

    def __init__(self, qubits: QubitSet = DummyQubitSet(), space: int = __DEFAULT_SPACE,
                 max_energy: int = __DEFAULT_MAX_ENERGY, start_energy: int = None):
        """

        :param qubits: the QubitSet the Robot is currently using
        :param space: how many instructions the robot can put on their circuit
        :param max_energy: how much energy the robot can store at most
        :param start_energy: with how much energy the robot starts. If it is bigger than max_energy, max_energy will be
                             used instead of the specified number
        """
        if space is None:
            space = _Attributes.__DEFAULT_SPACE
        if max_energy is None:
            max_energy = _Attributes.__DEFAULT_MAX_ENERGY
        if start_energy is None:
            start_energy = max_energy

        assert space > 0
        assert max_energy > _Attributes.__MIN_INIT_ENERGY
        assert start_energy > _Attributes.__MIN_INIT_ENERGY

        self.__qubits: QubitSet = qubits
        self.__space: int = space
        self.__max_energy: int = max_energy
        self.__cur_energy: int = min(start_energy, max_energy)

    @property
    def num_of_qubits(self) -> int:
        """

        :return: number of qubits the Robot's QubitSet has
        """
        return self.__qubits.size

    @property
    def circuit_space(self) -> int:
        """

        :return: maximum number of Instructions the Robot can use in its Circuit
        """
        return self.__space

    @property
    def qubits(self) -> QubitSet:
        """

        :return: the QubitSet used by the Robot
        """
        return self.__qubits

    @property
    def cur_energy(self) -> int:
        """

        :return: the amount of energy the Robot currently has
        """
        return self.__cur_energy

    @property
    def max_energy(self) -> int:
        """

        :return: the maximum amount of energy the Robot can store
        """
        return self.__max_energy

    def add_qubits(self, additional_qubits: int = 1):
        """
        Adds the given number of additional qubits to the QubitSet.

        :param additional_qubits: how many qubits to add (defaults to 1)
        :return: None
        """
        self.__qubits = self.__qubits.add_qubits(additional_qubits)

    def update_circuit_space(self, new_space: int) -> bool:
        if new_space <= 0: return False

        self.__space = new_space
        return True

    def increase_energy(self, amount: int) -> int:
        """
        Increases current energy by the given amount up to maximum energy.

        :param amount: by how much we want to increase current energy
        :return: by how much current energy was actually increased
        """
        self.__cur_energy += amount
        if self.__cur_energy > self.__max_energy:
            overflow = self.__cur_energy - self.__max_energy
            amount -= overflow
            self.__cur_energy = self.__max_energy
        return amount

    def decrease_energy(self, amount: int) -> int:
        """
        Decreases current energy by the given amount at most to 0.

        :param amount: by how much we want to decrease current energy
        :return: by how much current energy was actually decreased
        """
        if CheatConfig.got_inf_resources():
            return 0  # no decrease in this case

        self.__cur_energy -= amount
        if self.__cur_energy < 0:
            # e.g. if we decrease by 6 then cur_energy is now -2, so actually we were only able to decrease it by 4
            amount += self.__cur_energy
            self.__cur_energy = -1
        return amount


class _Backpack:
    """
    Stores Instructions, Consumables and other Collectibles for a Robot to use.
    """

    __DEFAULT_CAPACITY: int = 5  # how many Instructions the Backpack can hold at once

    def __init__(self, capacity: Optional[int] = None, content: Optional[List[Instruction]] = None):
        """
        Backpack is a storage/management class for Collectibles.

        :param capacity: how many Instructions can be stored in this Backpack
        :param content: list of initially stored Instructions
        """
        if capacity is None:
            capacity = _Backpack.__DEFAULT_CAPACITY

        self.__capacity: int = capacity
        if content:
            # self.__capacity = max(len(content), capacity)
            self.__storage: List[Instruction] = content
        else:
            self.__capacity = capacity
            self.__storage: List[Instruction] = []
        self.__key_count: int = 0

    @property
    def capacity(self) -> int:
        """

        :return: how many Collectibles can be stored in this Backpack
        """
        return self.__capacity

    @property
    def used_capacity(self) -> int:
        """

        :return: number of items currently stored
        """
        return len(self.__storage)

    @property
    def key_count(self) -> int:
        """

        :return: number of Keys we currently have
        """
        if CheatConfig.got_inf_resources():
            return 999
        return self.__key_count

    def give_key(self, amount: int) -> bool:
        """
        Adds the given amount of Keys. Fails if amount is less or equal to 0.

        :param amount: how many Keys we want to add
        :return: True if the given amount of Keys where handed out successfully, False otherwise
        """
        if amount > 0:
            self.__key_count += amount
            return True
        return False

    def use_key(self) -> bool:
        """
        Uses one Key, i.e. decreases key count by 1.

        :return: True if we could successfully use a Key, False if it failed (e.g. no Key left)
        """
        if CheatConfig.got_inf_resources():
            return True

        if self.key_count > 0:
            self.__key_count -= 1
            return True
        return False

    def get(self, index: int) -> Optional[Instruction]:
        """
        Returns the Instruction at the provided index in the storage if index is valid. Otherwise returns None.

        :param index: index of the Instruction we want to get
        :return: the Instruction at the given index or None
        """
        if 0 <= index < self.used_capacity:
            return self.__storage[index]
        return None

    def add(self, instruction: Instruction, force: bool = False) -> bool:
        """
        Adds an Instruction to the backpack if possible (i.e. if there is still space left).

        :param instruction: the Instruction to add
        :param force: whether we force instruction to be added, defaults to False
        :return: True if there is enough capacity left to store the Instruction, False otherwise
        """
        if self.used_capacity < self.__capacity or force:
            self.__storage.append(instruction)
            return True
        return False

    def remove(self, instruction: Instruction) -> bool:
        """
        Removes a given Instruction from the backpack if it's actually stored in it.

        :param instruction: the Instruction we want to remove
        :return: True if the Instruction is in the backpack and we were able to remove it, False otherwise
        """
        for i in range(len(self.__storage)):
            if self.__storage[i] == instruction:
                self.__storage.remove(instruction)
                return True
        if Config.debugging():
            Logger.instance().error("Reached a line in Backpack.remove() that I think should not be reachable ("
                                    "although it has no game-consequences if I'm wrong).", show=False, from_pycui=False)
        try:
            self.__storage.remove(instruction)
            return True
        except ValueError:
            return False

    def set_instructions(self, gate_list: List[Instruction]) -> bool:
        """
        Clears the stored Instructions and stores copies of all Instructions in gate_list.

        :param gate_list: the instructions to store
        :return: True if gates were stored correctly, False otherwise (e.g., more gates than $capacity were provided)
        """
        if 0 <= len(gate_list) < self.capacity:
            self.__storage.clear()
            for gate in gate_list:
                self.__storage.append(gate.copy())
            return True
        return False

    def copy_gates(self) -> List[Instruction]:
        """
        Creates a new List that contains copies of all the stored gates.

        :return: a deep copy of the stored gates
        """
        data = []
        for gate in self.__storage:
            data.append(gate.copy())
        return data  # [gate.copy() for gate in self.__storage]

    def instruction_iterator(self) -> Iterator[Instruction]:
        """

        :return: an Iterator over the stored Instructions
        """
        return iter(self.__storage)


class Robot(Controllable, ABC):
    @staticmethod
    def __counts_to_bit_list(counts):  # todo can be deleted I think
        counts = str(counts)
        counts = counts[1:len(counts) - 1]
        arr = counts.split(':')
        if int(arr[1][1:]) != 1:
            Logger.instance().throw(ValueError(f"Function only works for counts with 1 shot but counts was: {counts}"))
        bits = arr[0]
        bits = bits[1:len(bits) - 1]
        list_ = []
        for b in bits:
            list_.append(int(b))
        list_.reverse()  # so that list_[i] corresponds to the measured value of qi
        return list_

    def __init__(self, name: str, attributes: _Attributes, backpack: _Backpack, game_over_callback: Callable[[], None]):
        """

        :param name: name of the Robot for identification and rendering
        :param attributes: describes certain attributes of the Robot
        :param backpack: stores Collectibles
        :param game_over_callback: for stopping the game if the Robot dies
        """
        super().__init__(name)
        self.__score: int = 0
        self.__attributes: _Attributes = attributes
        self.__backpack: _Backpack = backpack
        self.__game_over: Callable[[], None] = game_over_callback
        # initialize qubit stuff (rows)
        self.__simulator = QuantumSimulator()
        self.__unitary_simulator = UnitarySimulator()
        self.__stv: Optional[StateVector] = None
        self.__circuit_matrix: Optional[CircuitMatrix] = None
        self.__qubit_indices: List[int] = []
        for i in range(0, attributes.num_of_qubits):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        self.__instruction_count: int = 0  # how many instructions are currently placed on the circuit
        # initialize based on empty circuit
        self.__instructions: List[Optional[Instruction]] = [None] * attributes.circuit_space
        # initially there is no static gate (i.e., a gate that cannot be moved and was added by a puzzle)

        if False:
            # todo: for whatever reason this code is slower than calling below method which executes a simulation...
            # todo: (measured execution time is faster, but something is slowed down because the startup time of levels increases)
            self.__stv = StateVector.create_zero_state_vector(self.num_of_qubits)
            self.__circuit_matrix = CircuitMatrix.create_identity(self.num_of_qubits)
        else:
            self.update_statevector(None, use_energy=False, check_for_game_over=False)

    @property
    def used_capacity(self) -> int:
        """
        :return: how many instructions are placed on the robot's circuit
        """
        return self.__backpack.used_capacity

    @property
    def capacity(self) -> int:
        """
        :return: how many instructions can be placed on the robot's circuit
        """
        return self.__backpack.capacity

    @property
    def instructions(self) -> Iterator[Instruction]:
        return self.__backpack.instruction_iterator()

    @property
    def state_vector(self) -> StateVector:
        return self.__stv

    @property
    def circuit_matrix(self) -> CircuitMatrix:
        return self.__circuit_matrix

    @property
    def score(self) -> int:
        return self.__score

    @property
    def cur_energy(self) -> int:
        return self.__attributes.cur_energy

    @property
    def max_energy(self) -> int:
        return self.__attributes.max_energy

    @property
    def num_of_qubits(self) -> int:
        return self.__attributes.num_of_qubits

    @property
    def has_empty_circuit(self) -> bool:
        return self.__instruction_count == 0

    @property
    def circuit_space(self) -> int:
        return self.__attributes.circuit_space

    @property
    def is_space_left(self) -> bool:
        """

        :return: True if the backpack has still space for new Instructions, False if it's already full
        """
        return self.__instruction_count < self.circuit_space

    def game_over_check(self) -> bool:
        """
        Checks if the Robot still has some energy and then calls game_over() if there is None left.

        :return: True if the Robot is game over, False otherwise
        """
        if self.cur_energy <= 0:
            self.__game_over()
            return True
        return False

    def increase_score(self, amount: int):
        if amount < 0:
            Logger.instance().error(f"Tried to increase score by a negative amount: {amount}!", show=False,
                                    from_pycui=False)
            return
        self.__score += amount

    def reset_score(self):
        self.__score = 0

    def key_count(self) -> int:  # cannot be a property since it is an abstractmethod in Controllable
        return self.__backpack.key_count

    def use_key(self) -> bool:
        return self.__backpack.use_key()

    def __update_circuit_space(self, new_circuit_space: int):
        old_instructions = self.__instructions.copy()

        self.__instructions: List[Optional[Instruction]] = [None] * new_circuit_space
        self.__attributes.update_circuit_space(new_circuit_space)

        # copy all placed instructions
        for i, inst in enumerate(old_instructions):
            if inst is not None and i < len(self.__instructions):
                self.__instructions[i] = inst

    def update_statevector(self, input_stv: StateVector, use_energy: bool = True, check_for_game_over: bool = True):
        """
        Compiles and simulates the current circuit and saves and returns the resulting StateVector. Can also lead to a
        game over.

        :param input_stv: custom StateVector used as input
        :param use_energy: whether the update should cost energy or not, defaults to True
        :param check_for_game_over: whether we should perform a game over check or not
        :return: None
        """
        if check_for_game_over and self.game_over_check():
            return

        num_of_used_gates: int = 0  # cannot use len(instructions) since this contains None values
        circuit = QuantumCircuit.from_bit_num(self.num_of_qubits, self.num_of_qubits)
        for inst in self.__instructions:
            if inst is not None:
                num_of_used_gates += 1
                inst.append_to(circuit)

        amplitudes = self.__unitary_simulator.execute(circuit, decimals=QuantumSimulationConfig.DECIMALS)
        self.__circuit_matrix = CircuitMatrix(amplitudes, num_of_used_gates)

        if input_stv is None:  # todo: input_stv might only be None if the circuit is empty (reset or initialized)
            amplitudes = self.__simulator.run(circuit, do_transpile=True)
            self.__stv = StateVector(amplitudes, num_of_used_gates=self.__instruction_count)
        else:
            self.__stv = self.__circuit_matrix.multiply(input_stv)
            if self.__stv is None:
                self.__stv = StateVector.create_zero_state_vector(self.num_of_qubits)

        if use_energy and GameplayConfig.get_option_value(Options.energy_mode):
            self.decrease_energy(amount=1)

    def __remove_instruction(self, instruction: Optional[Instruction], skip_qargs: bool = False) -> bool:
        """
        Tries to remove the given instruction from the circuit. Fails if the Instruction is not used in the circuit.

        :param instruction: the Instruction to remove
        :param skip_qargs: whether to skip resetting the qubits of the Instruction or not, defaults to False
        :return: True if we successfully removed the Instruction, False otherwise
        """
        # todo check if we can extend the condition with "and instruction in self.__instructions"
        if instruction and instruction.is_used():
            self.__instructions[instruction.position] = None
            self.__instruction_count -= 1
            instruction.reset(skip_qargs=skip_qargs)
            return True
        return False

    def remove_instruction(self, instruction: Instruction) -> bool:
        """
        Tries to remove the given instruction from the circuit.

        :param instruction: the Instruction to remove
        :return: True if we successfully removed the Instruction, False otherwise
        """
        if instruction in self.__instructions:
            return self.__remove_instruction(instruction)
        return False

    def __place_instruction(self, instruction: Instruction, position: int) -> bool:
        """
        Tries to place the given instruction at the given position.

        :param instruction: the Instruction we want to place
        :param position: the position in the circuit where we want to place instruction at
        :return: True if instruction was successfully placed at position, False otherwise
        """
        if instruction.position == position:
            return True  # nothing to do in this case
        if instruction.is_used():
            Logger.instance().throw(RuntimeError("Illegal state: Instruction was not removed before placing!"))
            return False

        if 0 <= position < self.circuit_space:
            if self.__instructions[position]:
                self.__remove_instruction(self.__instructions[position])
            self.__instruction_count += 1
            self.__instructions[position] = instruction
            return instruction.use(position)
        else:
            # illegal position removes the instruction from the circuit if possible
            self.__remove_instruction(instruction)
            return False

    def __move_instruction(self, instruction: Instruction, position: int) -> bool:
        """
        Tries to move instruction to position. Fails if instruction is not used or already at position. If an invalid
        position is given, instruction is removed instead.

        :param instruction: the Instruction we want to move
        :param position: the position to which we want to move instruction (invalid position => remove)
        :return: True if we successfully (re)moved instruction, False otherwise
        """
        if instruction.is_used() and instruction.position != position:
            if 0 <= position < self.circuit_space:
                if self.__instructions[position]:
                    self.__remove_instruction(instruction, skip_qargs=True)
                    self.__remove_instruction(self.__instructions[position])
                else:
                    self.__remove_instruction(instruction, skip_qargs=True)
                return self.__place_instruction(instruction, position)
            else:
                self.__remove_instruction(instruction)
                return True
        return False

    def get_stored_instruction(self, index: int) -> Optional[Instruction]:
        """
        Returns the Instruction stored at the given index in the backpack or None for invalid indices.

        :param index: index of the Instruction in the backpack
        :return: the stored Instruction at the given index or None
        """
        if 0 <= index < self.__backpack.used_capacity:
            return self.__backpack.get(index)
        return None

    def use_instruction(self, instruction: Instruction, position: int) -> bool:
        """
        Tries to put the Instruction corresponding to the given index in the backpack into the robot's circuit.
        If the Instruction is already in-use (put onto the circuit) it is removed instead.

        :param instruction: the Instruction we want to use
        :param position: the position of the Instruction in the circuit
        :return: True if we were able to use the Instruction in our circuit
        """
        if instruction.is_used():
            self.__move_instruction(instruction, position)
        else:
            if self.is_space_left or GameplayConfig.get_option_value(Options.allow_implicit_removal):
                return self.__place_instruction(instruction, position)
            else:
                return False
        return True

    def reset_circuit(self):
        """
        Resets the circuit by removing all Instructions of it and updating the statevector.

        :return: None
        """
        temp = self.__instructions.copy()
        for instruction in temp:
            self.__remove_instruction(instruction)
        self.__instruction_count = 0
        self.__stv = StateVector.create_zero_state_vector(self.num_of_qubits)
        self.__circuit_matrix = CircuitMatrix.create_identity(self.num_of_qubits)

    def get_available_instructions(self) -> List[Instruction]:
        """

        :return: a List containing copies of all Instructions currently available to this Robot
        """
        return self.__backpack.copy_gates()

    def set_available_instructions(self, gates: Union[List[Instruction], List[GateType]]) -> bool:
        """
        :param gates: either a list of GateType or Instruction that determines which Instructions are available
        :return: True if gates were successfully set, False if an error occurred
        """
        if len(gates) > 0 and isinstance(gates[0], GateType):
            gate_types: List[GateType] = gates
            gates = [InstructionManager.from_type(gt) for gt in gate_types]
        return self.__backpack.set_instructions(gates)

    def give_collectible(self, collectible: Collectible, force: bool = False) -> bool:
        """
        Gives collectible to this Robot.

        :param collectible: the Collectible we want to give this Robot
        :param force: whether we force collectible to be added, defaults to False
        :return: True if the collectible was given successfully, False otherwise
        """
        if isinstance(collectible, Score):
            self.__score += collectible.amount
            return True
        elif isinstance(collectible, Key):
            return self.__backpack.give_key(collectible.amount)
        elif isinstance(collectible, Energy):
            self.__attributes.increase_energy(collectible.amount)
            return True
        elif isinstance(collectible, Instruction):
            return self.__backpack.add(collectible, force)
        elif isinstance(collectible, Qubit):
            self.__attributes.add_qubits(collectible.additional_qubits)
            return True
        elif isinstance(collectible, MultiCollectible):
            success = True
            for c in collectible.iterator():
                success = success and self.give_collectible(c, force)
            return success
        else:
            Logger.instance().error(f"Received uncovered collectible: {collectible}", show=False, from_pycui=False)
            return False

    def on_move(self):
        """
        Does nothing now!
        No longer decreases energy every time the Robot moves. This feature turned out to be tedious and doesn't
        support the game's goal of making you familiar with Quantum Computing in any way.

        :return: None
        """
        # self.__attributes.decrease_energy(amount=1)
        pass

    def decrease_energy(self, amount: int = 1) -> Tuple[int, bool]:
        """
        Decreases this Robot's current energy by the given amount.

        :param amount: by how much we want to reduce this Robot's energy, defaults to 1
        :return: the actual amount by how much current energy was decreased, whether this Robot is game over or not
        """
        assert amount > 0  # todo maybe == 0 is also okay?

        if self.game_over_check():
            return amount, True
        return self.__attributes.decrease_energy(amount), False

    def increase_energy(self, amount: int = 1) -> int:
        """
        Increases this Robot's current energy by the given amount at most to its max energy.

        :param amount: by how much current energy was increased
        :return: by how much current energy was actually increased.
        """
        assert amount > 0  # todo maybe == 0 is also okay?
        return self.__attributes.increase_energy(amount)

    def gate_used_at(self, position: int) -> Optional[Instruction]:
        """
        Returns the Instruction at the given index or None for invalid indices.

        :param position: position of the Instruction in the circuit
        :return: the Instruction at the given position or None
        """
        if 0 <= position < self.circuit_space:
            return self.__instructions[position]
        return None

    def reset(self):
        self.__attributes.increase_energy(self.__attributes.max_energy)
        self.reset_circuit()


class BaseBot(Robot):
    @staticmethod
    def from_properties(properties: RoboProperties, game_over_callback: Callable[[], None]) -> "BaseBot":
        return BaseBot(game_over_callback, num_of_qubits=properties.num_of_qubits,
                       circuit_space=properties.circuit_space, gates=properties.instruction_list)

    def __init__(self, game_over_callback: Callable[[], None], num_of_qubits: int = 3,
                 gates: Optional[List[Instruction]] = None,
                 circuit_space: Optional[int] = None, backpack_space: Optional[int] = None,
                 max_energy: Optional[int] = None, start_energy: Optional[int] = None):
        attributes = _Attributes(DummyQubitSet(num_of_qubits), circuit_space, max_energy, start_energy)
        backpack = _Backpack(backpack_space, gates)
        super(BaseBot, self).__init__("BaseBot", attributes, backpack, game_over_callback)

    def get_img(self):
        return "Q"

    def description(self) -> str:
        return "The most basic Robot"


class LukeBot(Robot):
    def __init__(self, game_over_callback: Callable[[], None], size: int = 2):
        attributes = _Attributes(DummyQubitSet(size))
        backpack = _Backpack(capacity=5)

        # randomness is not allowed during Robot creation because it messes up the seed
        # add random gates and a HealthPotion
        # rm = RandomManager.create_new()
        # if rm.get(msg="LukeBot.init()") < 0.5:
        #     num_of_gates = 3
        # else:
        #     num_of_gates = 4
        # gate_factory = GateFactory.default()
        # for gate in gate_factory.produce_multiple(rm, num_of_gates):
        #     backpack.add(gate)
        # backpack.place_in_pouch(HealthPotion(3))
        super().__init__("Luke", attributes, backpack, game_over_callback)

    def get_img(self):
        return "L"

    def description(self) -> str:
        return "The loyal Robot you start with. A true all-rounder - take good care of it!"
