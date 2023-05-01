"""
Author: Artner Michael
13.06.2021
"""
from abc import ABC
from typing import Tuple, List, Callable, Optional, Union, Set

from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import StatevectorSimulator

from qrogue.game.logic.actors import StateVector, CircuitMatrix
from qrogue.game.logic.actors.controllables import Controllable
from qrogue.game.logic.actors.controllables.qubit import QubitSet, DummyQubitSet
from qrogue.game.logic.collectibles import Coin, Collectible, Consumable, Instruction, Key, MultiCollectible, \
    Qubit, Energy
from qrogue.util import CheatConfig, Config, Logger, GameplayConfig, QuantumSimulationConfig, Options


# from jkq import ddsim


class _Attributes:
    """
    A class that handles some attributes of a Robot.
    """

    __DEFAULT_SPACE = 3
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
            return 0    # no decrease in this case

        self.__cur_energy -= amount
        if self.__cur_energy < 0:
            # e.g. if we decrease by 6 then cur_energy is now -2, so actually we were only able to decrease it by 4
            amount += self.__cur_energy
            self.__cur_energy = -1
        return amount


class Backpack:
    """
    Stores Instructions, Consumables and other Collectibles for a Robot to use.
    """

    __CAPACITY: int = 5      # how many Instructions the Backpack can hold at once
    __POUCH_SIZE: int = 5    # how many Consumables the Backpack can hold at once

    def __init__(self, capacity: int = __CAPACITY, content: Optional[List[Instruction]] = None):
        """
        Backpack is a storage/management class for Collectibles.

        :param capacity: how many Instructions can be stored in this Backpack
        :param content: list of initially stored Instructions
        """
        if capacity is None:
            capacity = Backpack.__CAPACITY

        self.__capacity: int = capacity
        if content:
            # self.__capacity = max(len(content), capacity)
            self.__storage: List[Instruction] = content
        else:
            self.__capacity = capacity
            self.__storage: List[Instruction] = []
        self.__pouch_size: int = Backpack.__POUCH_SIZE
        self.__pouch: List[Consumable] = []
        self.__coin_count: int = 0
        self.__key_count: int = 0

    def __iter__(self) -> "BackpackIterator":
        """

        :return: an Iterator over the stored Instructions
        """
        return BackpackIterator(self)

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
    def consumables_in_pouch(self) -> int:
        """

        :return: how many Consumables are currently stored
        """
        return len(self.__pouch)

    @property
    def num_of_available_items(self) -> int:
        """

        :return: number of items that are currently available to use (e.g. Consumables)
        """
        return self.consumables_in_pouch    # later we might add active item(s)?

    @property
    def coin_count(self) -> int:
        """

        :return: number of Coins we currently have
        """
        if CheatConfig.got_inf_resources():
            return 999
        return self.__coin_count

    @property
    def key_count(self) -> int:
        """

        :return: number of Keys we currently have
        """
        if CheatConfig.got_inf_resources():
            return 999
        return self.__key_count

    def can_afford(self, price: int) -> bool:
        """
        Checks if we have enough resources to afford a Collectible with the given price.

        :param price: how many Coins the item costs
        :return: whether we could afford a Collectible with this price or not
        """
        return self.coin_count >= price

    def give_coin(self, amount: int) -> bool:
        """
        Adds the given amount of Coins. Fails if amount is less or equal to 0.

        :param amount: how many Coins we want to add
        :return: True if the given amount of Coins is handed out successfully, False otherwise
        """
        if amount > 0:
            self.__coin_count += amount
            return True
        return False

    def spend_coins(self, amount: int) -> bool:
        """
        Spends the given amount of Coins, i.e. decreases coin count by the given amount.

        :param amount: how many Coins we want to spend
        :return: True if we could successfully spend the amount of Coins, False if it failed (e.g. not enough Coins)
        """
        if CheatConfig.got_inf_resources():
            return True

        if self.can_afford(amount):
            self.__coin_count -= amount
            return True
        return False

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
        Returns the Instruction at the provided index in the storage if index is valid. Otherwise, returns None.

        :param index: index of the Instruction we want to get
        :return: the Instruction at the given index or None
        """
        if 0 <= index < self.used_capacity:
            return self.__storage[index]
        return None

    def add(self, instruction: Instruction) -> bool:
        """
        Adds an Instruction to the backpack if possible (i.e. if there is still space left).

        :param instruction: the Instruction to add
        :return: True if there is enough capacity left to store the Instruction, False otherwise
        """
        if self.used_capacity < self.__capacity:
            self.__storage.append(instruction)
            return True
        return False

    def remove(self, instruction: Instruction) -> bool:
        """
        Removes a given Instruction from the backpack if it's actually stored in it.

        :param instruction: the Instruction we want to remove
        :return: True if the Instruction is in the backpack, and we were able to remove it. False otherwise.
        """
        for i in range(len(self.__storage)):
            if self.__storage[i] == instruction:
                self.__storage.remove(instruction)
                return True
        if Config.debugging():
            Logger.instance().error("Reached a line in Backpack.remove() that I think should not be reachable "
                                    "(although it has no game-consequences if I'm wrong).", from_pycui=False)
        try:
            self.__storage.remove(instruction)
            return True
        except ValueError:
            return False

    def pouch_iterator(self) -> __iter__:
        """

        :return: an Iterator over the Consumables stored in this Backpack
        """
        return iter(self.__pouch)

    def get_from_pouch(self, index: int) -> Optional[Consumable]:
        """
        Returns the Consumable at the provided index in the pouch if index is valid. Otherwise, returns None.

        :param index: index of the Consumable we want to get
        :return: the Consumable at the given index or None
        """
        if 0 <= index < self.consumables_in_pouch:
            return self.__pouch[index]
        return None

    def place_in_pouch(self, consumable: Consumable) -> bool:
        """
        Places a Consumable in the pouch if possible (i.e. there is still space left).

        :param consumable: the Consumable we want to store in the pouch
        :return: True if we could add the Consumable, False otherwise
        """
        if self.consumables_in_pouch < self.__pouch_size:
            self.__pouch.append(consumable)
            return True
        return False

    def remove_from_pouch(self, consumable: Consumable) -> bool:
        """
        Tries to remove a given Consumable from the pouch. Fails if it's not stored in the pouch.

        :param consumable: the Consumable we want to remove
        :return: True if consumable was removed successfully, False otherwise
        """
        try:
            self.__pouch.remove(consumable)
            return True
        except ValueError:
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


class BackpackIterator:
    """
    Allows us to easily iterate through all the Instructions in a backpack.
    """

    def __init__(self, backpack: Backpack):
        self.__index: int = 0
        self.__backpack: Backpack = backpack

    def __next__(self) -> Instruction:
        if self.__index < self.__backpack.used_capacity:
            item = self.__backpack.get(self.__index)
            self.__index += 1
            return item
        raise StopIteration


class Robot(Controllable, ABC):
    @staticmethod
    def __counts_to_bit_list(counts):       # todo can be deleted I think
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

    class CircuitGrid:
        class _CircuitGridIterator:
            def __init__(self, grid: "Robot.CircuitGrid"):
                self.__grid = grid
                self.__position = 0
                self.__qubit = 0
                self.__cur_gate: Optional[Instruction] = None

            def __next__(self):
                while self.__position < self.__grid.circuit_space:
                    while self.__qubit < self.__grid.num_of_qubits:
                        gate = self.__grid.get(self.__qubit, self.__position)
                        self.__qubit += 1  # proceed to next qubit

                        # for multi qubit gates we have to make sure to not return the same again
                        # doesn't work for three qubits yet! E.g.: CX @q0, H @q1, CX @q2        # todo
                        if gate is not None and gate != self.__cur_gate:
                            self.__cur_gate = gate
                            return self.__cur_gate

                    self.__qubit = 0  # reset qubit since we are done with the current position
                    self.__position += 1  # proceed to next position
                raise StopIteration

        def __init__(self, num_of_qubits: int, circuit_space: int):
            self.__num_of_qubits = num_of_qubits  # num of rows
            self.__circuit_space = circuit_space  # num of columns

            # rows have to be left-aligned with respect to their other qubits (i.e., no free space is allowed to be in
            # front of a single qubit gate)
            self.__grid: List[List[Optional[Instruction]]] = [[None] * circuit_space for _ in range(num_of_qubits)]
            self.__save_state: Optional[List[List[Optional[Instruction]]]] = None

        @property
        def num_of_qubits(self) -> int:
            return self.__num_of_qubits

        @property
        def circuit_space(self) -> int:
            return self.__circuit_space

        @property
        def is_empty(self) -> bool:
            return len(self) == 0

        @property
        def is_full(self) -> bool:
            for qu in range(self.__num_of_qubits):
                if self._has_qubit_free_space(qu):
                    return False
            return True

        def save(self):
            self.__save_state = []
            for row in self.__grid:
                self.__save_state.append(row.copy())

        def load(self):
            assert self.__save_state is not None, "Cannot load from None!"
            self.__grid = self.__save_state
            self.save()     # otherwise altering grid would influence save_state

        def remove(self, gate: Instruction) -> bool:
            place_data: List[Optional[int]] = []
            removal_failed = False
            for qubit in gate.qargs_iter():
                position = None
                for pos in range(self.__circuit_space):
                    val = self.__grid[qubit][pos]
                    if val == gate:
                        position = (qubit, pos)
                        break
                removal_failed = removal_failed or position is None  # once True, will stay True
                place_data.append(position)

            if removal_failed:
                return False
            else:
                for i, data in enumerate(place_data):
                    qu, pos = data
                    self.__grid[qu][pos] = None
                return True

        def __is_free(self, qubit: int, position: int) -> bool:
            assert 0 <= qubit < self.__num_of_qubits, \
                f"Qubit out of bounds: 0 <= {qubit} < {self.__num_of_qubits} is False!"
            assert 0 <= position < self.__circuit_space, \
                f"Position out of bounds: 0 <= {position} < {self.__circuit_space} is False!"
            return self.__grid[qubit][position] is None

        def _qubit_row(self, qubit: int) -> List[Optional[Instruction]]:
            assert 0 <= qubit < len(self.__grid)
            return self.__grid[qubit]

        def _num_of_gates_on_qubit(self, qubit: int) -> int:
            count = 0
            for val in self._qubit_row(qubit):
                if val is not None:
                    count += 1
            return count

        def _gate_at(self, qubit: int, position: int, relative: bool = True) -> Optional[Instruction]:
            if relative:
                assert 0 <= position < self._num_of_gates_on_qubit(qubit)
                count = -1
                for val in self._qubit_row(qubit):
                    if val is not None:
                        count += 1
                        if position == count:
                            return val
                return None
            else:
                assert 0 <= position < len(self._qubit_row(qubit))
                return self.__grid[qubit][position]

        def _find_pos_for(self, qubit: int, og_position: int):
            row = self.__grid[qubit]
            if og_position == 0:
                pass
            while True:
                pass

        def _has_qubit_free_space(self, qubit: int) -> bool:
            """
            Whether the given qubit (i.e., grid row) has still a free spot where we could place a gate at.
            """
            for val in self.__grid[qubit]:
                if val is None:
                    return True
            return False

        def get(self, qubit: int, position: int) -> Optional[Instruction]:
            assert 0 <= qubit < self.__num_of_qubits, \
                f"Qubit out of bounds: 0 <= {qubit} < {self.__num_of_qubits} is False!"
            assert 0 <= position < self.__circuit_space, \
                f"Position out of bounds: 0 <= {position} < {self.__circuit_space} is False!"

            return self.__grid[qubit][position]

        def place(self, gate: Instruction, position: int, overwrite: bool = True) -> bool:
            self.remove(gate)

            qubit = gate.qargs_copy()
            if isinstance(qubit, int): qubit = [qubit]
            assert len(qubit) == gate.num_of_qubits

            for qu in qubit:
                if not self._has_qubit_free_space(qu):
                    return False

            def first_free_spot(qubit_: int, og_pos: int) -> int:
                # search the first free spot in front of og_pos (or og_pos if nothing is free)
                og_pos -= 1
                while og_pos >= 0 and self.__grid[qubit_][og_pos] is None: og_pos -= 1
                # we either stopped because there is a gate at og_pos (hence we increase it again) or because og_pos < 0
                return og_pos + 1

            def shift_right(qubit_: int, og_pos: int):
                if self.__grid[qubit_][og_pos] is None:
                    return  # no need to shift

                # find the left most free spot after og_pos
                index = og_pos + 1
                while index < self.__circuit_space and self.__grid[qubit_][index] is not None: index += 1
                # now go back to position and shift everything to the right by 1
                while index > og_pos:
                    self.__grid[qubit_][index] = self.__grid[qubit_][index - 1]
                    index -= 1

            if gate.num_of_qubits == 1:
                qubit = qubit[0]
                position = first_free_spot(qubit,
                                           position)  # align it to the left by finding the left most viable position
                shift_right(qubit, position)  # does nothing if the corresponding spot is free
                self.__grid[qubit][position] = gate
            else:
                left_most_positions = [first_free_spot(qu, position) for qu in qubit]
                position = max(left_most_positions)
                for qu in qubit:
                    shift_right(qu, position)  # todo cannot shift multi-qubit gates yet!
                    self.__grid[qu][position] = gate

            return True

        def clear(self):
            pass

        def __len__(self):
            # todo test method!
            gates: Set[Instruction] = set()
            for qu in range(self.__num_of_qubits):
                for pos in range(self.__circuit_space):
                    # we have to iterate over the whole circuit space since multi qubit gates can create empty spaces
                    # in the middle of a row (even though we always shift to the left as far as possible)
                    gates.add(self.get(qu, pos))
            return len(gates)

        def __iter__(self):
            return Robot.CircuitGrid._CircuitGridIterator(self)

        def __str__(self):
            text = ""
            for row in self.__grid:
                for val in row:
                    if val is None:
                        text += "---"
                    else:
                        text += f"-{val}-"
                text += "\n"
            return text

    def __init__(self, name: str, attributes: _Attributes, backpack: Backpack, game_over_callback: Callable[[], None]):
        """

        :param name: name of the Robot for identification and rendering
        :param attributes: describes certain attributes of the Robot
        :param backpack: stores Collectibles
        :param game_over_callback: for stopping the game if the Robot dies
        """
        super().__init__(name)
        self.__attributes: _Attributes = attributes
        self.__backpack: Backpack = backpack
        self.__game_over: Callable[[], None] = game_over_callback
        # initialize qubit stuff (rows)
        self.__simulator = StatevectorSimulator()  # ddsim.JKQProvider().get_backend('statevector_simulator')
        self.__backend = Aer.get_backend('unitary_simulator')
        self.__stv: Optional[StateVector] = None
        self.__circuit_matrix: Optional[CircuitMatrix] = None
        self.__qubit_indices: List[int] = []
        for i in range(0, attributes.num_of_qubits):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        # apply gates/instructions, create the circuit
        self.__instructions = Robot.CircuitGrid(self.__attributes.num_of_qubits, self.__attributes.circuit_space) #LinkedList(capacity=self.__attributes.circuit_space)
        self.update_statevector(use_energy=False, check_for_game_over=False)  # to initialize the statevector

    @property
    def backpack(self) -> Backpack:
        return self.__backpack

    @property
    def grid(self) -> CircuitGrid:
        return self.__instructions

    @property
    def state_vector(self) -> StateVector:
        return self.__stv

    @property
    def circuit_matrix(self) -> CircuitMatrix:
        return self.__circuit_matrix

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
        return self.__instructions.is_empty

    @property
    def circuit_space(self) -> int:
        return self.__attributes.circuit_space

    @property
    def is_space_left(self) -> bool:
        """

        :return: True if the backpack has still space for new Instructions, False if it's already full
        """
        return not self.__instructions.is_full

    def game_over_check(self) -> bool:
        """
        Checks if the Robot still has some energy and then calls game_over() if there is None left.

        :return: True if the Robot is game over, False otherwise
        """
        if self.__attributes.cur_energy <= 0:
            self.__game_over()
            return True
        return False

    def key_count(self) -> int:     # cannot be a property since it is an abstractmethod in Controllable
        return self.backpack.key_count

    def use_key(self) -> bool:
        return self.backpack.use_key()

    def update_statevector(self, use_energy: bool = True, check_for_game_over: bool = True):
        """
        Compiles and simulates the current circuit and saves and returns the resulting StateVector. Can also lead to a
        game over.

        :param use_energy: whether the update should cost energy or not, defaults to True
        :param check_for_game_over: whether we should perform a game over check or not
        :return: None
        """
        if check_for_game_over and self.game_over_check():
            return

        circuit = QuantumCircuit(self.__attributes.num_of_qubits, self.__attributes.num_of_qubits)
        for inst in self.__instructions: inst.append_to(circuit)

        compiled_circuit = transpile(circuit, self.__simulator)
        job = self.__simulator.run(compiled_circuit, shots=1)
        result = job.result()
        self.__stv = StateVector(result.get_statevector(circuit), num_of_used_gates=len(self.__instructions))

        job = execute(circuit, self.__backend)
        result = job.result()
        self.__circuit_matrix = CircuitMatrix(result.get_unitary(circuit,
                                                                 decimals=QuantumSimulationConfig.DECIMALS).data)
        if use_energy and GameplayConfig.get_option_value(Options.energy_mode):
            self.decrease_energy(amount=1)

    def __remove_instruction(self, instruction: Optional[Instruction], skip_qargs: bool = False) -> bool:
        """
        Tries to remove the given instruction from the circuit. Fails if the Instruction is not used in the circuit.

        :param instruction: the Instruction to remove
        :param skip_qargs: whether to skip resetting the qubits of the Instruction or not, defaults to False
        :return: True if we successfully removed the Instruction, False otherwise
        """
        if instruction is not None and instruction.is_used():
            Logger.instance().assertion(self.__instructions.remove(instruction), "Failed to remove a used instruction!")
            instruction.reset(skip_qargs=skip_qargs)
            return True
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

        if 0 <= position < self.__attributes.circuit_space:
            inst = self.__instructions.get(instruction.qargs_copy()[0], position)
            if inst is not None:    # todo
                self.__remove_instruction(inst)
            self.__instructions.place(instruction, position, overwrite=True)
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
            if 0 <= position < self.__attributes.circuit_space:
                inst = self.__instructions.get(instruction.qargs_copy()[0], position)   # todo check .get()
                if inst is not None:
                    self.__remove_instruction(instruction, skip_qargs=True)
                    self.__remove_instruction(inst)
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
        if 0 <= index < self.backpack.used_capacity:
            return self.backpack.get(index)
        return None

    def remove_instruction(self, instruction: Instruction) -> bool:
        """
        Tries to remove the given instruction from the circuit.

        :param instruction: the Instruction to remove
        :return: True if we successfully removed the Instruction, False otherwise
        """
        if instruction in self.__instructions:
            return self.__remove_instruction(instruction)
        return False

    def use_instruction(self, instruction: Instruction, position: int) -> bool:
        """
        Tries to put the given Instruction into the robot's circuit at the given position.
        If the Instruction is already in-use (put onto the circuit) it is removed instead.

        :param instruction: the Instruction we want to use
        :param position: the position of the Instruction in the circuit
        :return: True if we were able to use the Instruction in our circuit
        """
        if instruction.is_used():
            self.__remove_instruction(instruction)
            # self.__move_instruction(instruction, position)
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
        for instruction in self.__instructions:
            instruction.reset(skip_qargs=False)
        self.__instructions.clear()
        self.update_statevector(use_energy=False, check_for_game_over=False)

    def get_available_instructions(self) -> List[Instruction]:
        """

        :return: a List containing copies of all Instructions currently available to this Robot
        """
        return self.backpack.copy_gates()

    def give_collectible(self, collectible: Collectible):
        """
        Gives collectible to this Robot.

        :param collectible: the Collectible we want to give this Robot
        :return: None
        """
        if isinstance(collectible, Coin):
            self.backpack.give_coin(collectible.amount)
        elif isinstance(collectible, Key):
            self.backpack.give_key(collectible.amount)
        elif isinstance(collectible, Energy):
            self.__attributes.increase_energy(collectible.amount)
        elif isinstance(collectible, Instruction):
            self.backpack.add(collectible)
        elif isinstance(collectible, Consumable):
            self.backpack.place_in_pouch(collectible)
        elif isinstance(collectible, Qubit):
            self.__attributes.add_qubits(collectible.additional_qubits)
        elif isinstance(collectible, MultiCollectible):
            for c in collectible.iterator():
                self.give_collectible(c)
        else:
            Logger.instance().error(f"Received uncovered collectible: {collectible}", from_pycui=False)

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
        assert amount > 0   # todo maybe == 0 is also okay?

        if self.game_over_check():
            return amount, True
        return self.__attributes.decrease_energy(amount), False

    def increase_energy(self, amount: int = 1) -> int:
        """
        Increases this Robot's current energy by the given amount at most to its max energy.

        :param amount: by how much current energy was increased
        :return: by how much current energy was actually increased.
        """
        assert amount > 0   # todo maybe == 0 is also okay?
        return self.__attributes.increase_energy(amount)

    def gate_used_at(self, qubit: int, position: int) -> Optional[Instruction]:
        """
        Returns the Instruction at the given index or None for invalid indices.

        :param qubit:
        :param position: position of the Instruction in the circuit
        :return: the Instruction at the given position or None
        """
        if 0 <= position < self.circuit_space:
            return self.__instructions.get(qubit, position)
        return None

    def reset(self):
        self.__attributes.increase_energy(self.__attributes.max_energy)
        self.reset_circuit()


class BaseBot(Robot):
    def __init__(self, game_over_callback: Callable[[], None], num_of_qubits: int = 2,
                 gates: Optional[List[Instruction]] = None,
                 circuit_space: Optional[int] = None, backpack_space: Optional[int] = None,
                 max_energy: Optional[int] = None, start_energy: Optional[int] = None):
        attributes = _Attributes(DummyQubitSet(num_of_qubits), circuit_space, max_energy, start_energy)
        backpack = Backpack(backpack_space, gates)
        super(BaseBot, self).__init__("BaseBot", attributes, backpack, game_over_callback)

    def get_img(self):
        return "Q"

    def description(self) -> str:
        return "The most basic Robot"


class LukeBot(Robot):
    def __init__(self, game_over_callback: Callable[[], None], size: int = 2):
        attributes = _Attributes(DummyQubitSet(size))
        backpack = Backpack(capacity=5)

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
