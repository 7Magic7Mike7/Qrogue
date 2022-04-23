"""
Author: Artner Michael
13.06.2021
"""
from abc import ABC
from typing import Tuple, List, Callable

from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import StatevectorSimulator

from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.actors.controllables import Controllable
from qrogue.game.logic.collectibles import Coin, Collectible, Consumable, Instruction, Key, MultiCollectible, \
    Qubit, Energy
from qrogue.util import CheatConfig, Config, Logger, InstructionConfig, GameplayConfig

from .qubit import QubitSet, DummyQubitSet


# from jkq import ddsim


class _Attributes:
    __DAMAGE_TO_ENERGY = 10

    """
    Is used as storage for a bunch of attributes of the robot
    """

    def __init__(self, qubits: QubitSet = DummyQubitSet(), space: int = 3):
        """

        :param qubits: the set of qubits the robot is currently using
        :param space: how many instructions the robot can put on their circuit
        """
        self.__space = space
        self.__qubits = qubits
        self.__cur_energy = 1000
        self.__max_energy = 1000

    @property
    def is_alive(self) -> bool:
        return self.__cur_energy > 0

    @property
    def num_of_qubits(self) -> int:
        return self.__qubits.size

    @property
    def circuit_space(self) -> int:
        return self.__space

    @property
    def qubits(self) -> QubitSet:
        return self.__qubits

    @property
    def cur_energy(self) -> int:
        return self.__cur_energy

    @property
    def max_energy(self) -> int:
        return self.__max_energy

    def add_qubits(self, additional_qubits: int = 1):
        self.__qubits = self.__qubits.add_qubits(additional_qubits)

    def refill_energy(self, amount: int) -> int:
        self.__cur_energy += amount
        if self.__cur_energy > self.__max_energy:
            overflow = self.__cur_energy - self.__max_energy
            amount -= overflow
            self.__cur_energy = self.__max_energy
        return amount

    def decrease_energy(self, amount: int) -> Tuple[int, bool]:
        self.__cur_energy -= amount
        if self.__cur_energy < 0:
            amount += self.__cur_energy     # e.g. if we got 6 damage and cur_energy is now -2, we actually got 4 damage
            self.__cur_energy = 0
        return amount, not self.is_alive

    def damage(self, amount: int) -> Tuple[int, bool]:
        return self.decrease_energy(amount * _Attributes.__DAMAGE_TO_ENERGY)


class Backpack:
    """
    Stores Instructions, Consumables and other Collectibles for the robot to use.
    """
    __CAPACITY = 5      # how many Instructions the Backpack can hold at once
    __POUCH_SIZE = 5    # how many Consumables the Backpack can hold at once

    def __init__(self, capacity: int = __CAPACITY, content: List[Instruction] = None):
        """

        :param capacity: how many Instructions can be stored in this Backpack
        :param content: initially stored Instructions
        """
        self.__capacity = capacity
        if content:
            #self.__capacity = max(len(content), capacity)
            self.__storage = content
        else:
            self.__capacity = capacity
            self.__storage = []
        self.__pouch_size = Backpack.__POUCH_SIZE
        self.__pouch = []
        self.__coin_count = 0
        self.__key_count = 0

    def __iter__(self) -> "BackpackIterator":
        return BackpackIterator(self)

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def used_capacity(self) -> int:
        return len(self.__storage)

    @property
    def consumables_in_pouch(self) -> int:
        return len(self.__pouch)

    @property
    def num_of_available_items(self) -> int:
        return self.consumables_in_pouch    # later we might add active item(s)?

    @property
    def coin_count(self) -> int:
        if CheatConfig.got_inf_resources():
            return 999
        return self.__coin_count

    @property
    def key_count(self) -> int:
        if CheatConfig.got_inf_resources():
            return 999
        return self.__key_count

    def can_afford(self, price: int) -> bool:
        return self.coin_count >= price

    def give_coin(self, amount: int) -> bool:
        if amount > 0:
            self.__coin_count += amount
            return True
        return False

    def use_coins(self, amount: int) -> bool:
        if CheatConfig.got_inf_resources():
            return True

        if self.can_afford(amount):
            self.__coin_count -= amount
            return True
        return False

    def give_key(self, amount: int) -> bool:
        if amount > 0:
            self.__key_count += amount
            return True
        return False

    def use_key(self) -> bool:
        if CheatConfig.got_inf_resources():
            return True

        if self.key_count > 0:
            self.__key_count -= 1
            return True
        return False

    def get(self, index: int) -> Instruction:
        if 0 <= index < self.used_capacity:
            return self.__storage[index]

    def add(self, instruction: Instruction) -> bool:
        """
        Adds an Instruction to the backpack if possible.

        :param instruction: the Instruction to add
        :return: True if there is enough capacity left to store the Instruction, False otherwise
        """
        if self.used_capacity < self.__capacity:
            self.__storage.append(instruction)
            return True
        return False

    def remove(self, instruction: Instruction) -> bool:
        """
        Removes an Instruction from the backpack if it's present.

        :param instruction: the Instruction we want to remove
        :return: True if the Instruction is in the backpack and we were able to remove it, False otherwise
        """
        for i in range(len(self.__storage)):
            if self.__storage[i] == instruction:
                self.__storage.remove(instruction)
                return True
        if Config.debugging():
            Logger.instance().error("Reached a line in Backpack.remove() that I think should not be reachable "
                                    "(although it has no game-consequences if I'm wrong.")
        try:
            self.__storage.remove(instruction)
            return True
        except ValueError:
            return False

    def pouch_iterator(self) -> __iter__:
        return iter(self.__pouch)

    def get_from_pouch(self, index: int) -> Consumable:
        if 0 <= index < self.consumables_in_pouch:
            return self.__pouch[index]

    def place_in_pouch(self, consumable: Consumable) -> bool:
        if self.consumables_in_pouch < self.__pouch_size:
            self.__pouch.append(consumable)
            return True
        return False

    def remove_from_pouch(self, consumable: Consumable) -> bool:
        try:
            self.__pouch.remove(consumable)
            return True
        except ValueError:
            return False

    def copy_gates(self) -> [Instruction]:
        data = []
        for gate in self.__storage:
            data.append(gate.copy())
        return data #[gate.copy() for gate in self.__storage]


class BackpackIterator:
    """
    Allows us to easily iterate through all the Instructions in a backpack
    """
    def __init__(self, backpack: Backpack):
        self.__index = 0
        self.__backpack = backpack

    def __next__(self) -> Instruction:
        if self.__index < self.__backpack.used_capacity:
            item = self.__backpack.get(self.__index)
            self.__index += 1
            return item
        raise StopIteration


class Robot(Controllable, ABC):
    @staticmethod
    def __counts_to_bit_list(counts):
        counts = str(counts)
        counts = counts[1:len(counts) - 1]
        arr = counts.split(':')
        if int(arr[1][1:]) != 1:
            Logger.instance().throw(ValueError(f"Function only works for counts with 1 shot but counts was: {counts}"))
        bits = arr[0]
        bits = bits[1:len(bits) - 1]
        list = []
        for b in bits:
            list.append(int(b))
        list.reverse()  # so that list[i] corresponds to the measured value of qi
        return list

    def __init__(self, name: str, attributes: _Attributes, backpack: Backpack, game_over_callback: Callable[[], None]):
        super().__init__(name)
        self.__attributes = attributes
        self.__backpack = backpack
        self.__game_over = game_over_callback
        # initialize qubit stuff (rows)
        self.__simulator = StatevectorSimulator()#ddsim.JKQProvider().get_backend('statevector_simulator')
        self.__stv = None
        self.__qubit_indices = []
        for i in range(0, attributes.num_of_qubits):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        self.__instruction_count = 0

        # apply gates/instructions, create the circuit
        self.__circuit = None
        self.__instructions = [None] * attributes.circuit_space
        self.__apply_instructions()
        self.update_statevector()  # to initialize the statevector

    @property
    def backpack(self) -> Backpack:
        return self.__backpack

    @property
    def state_vector(self) -> StateVector:
        return self.__stv

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
        return self.__instruction_count < self.circuit_space

    def __apply_instructions(self):
        circuit = QuantumCircuit(self.__attributes.num_of_qubits, self.__attributes.num_of_qubits)
        for inst in self.__instructions:
            if inst:
                inst.append_to(circuit)
        self.__circuit = circuit
        return True

    def key_count(self) -> int:     # cannot be a property since it is an abstractmethod in Controllable
        return self.backpack.key_count

    def use_key(self) -> bool:
        return self.backpack.use_key()

    def update_statevector(self):
        """
        Compiles and simulates the current circuit and saves and returns the resulting StateVector
        :return: an updated StateVector corresponding to the current circuit
        """
        compiled_circuit = transpile(self.__circuit, self.__simulator)
        job = self.__simulator.run(compiled_circuit, shots=1)
        result = job.result()
        self.__stv = StateVector(result.get_statevector(self.__circuit))

    def __remove_instruction(self, instruction: Instruction, skip_qargs: bool = False):
        if instruction and instruction.is_used():
            self.__instructions[instruction.position] = None
            self.__instruction_count -= 1
            instruction.reset(skip_qargs=skip_qargs)

    def __place_instruction(self, instruction: Instruction, position: int):
        if instruction.position == position:
            return  # nothing to do in this case
        if instruction.is_used():
            Logger.instance().throw(RuntimeError("Illegal state: Instruction was not removed before placing!"))

        if 0 <= position < self.__attributes.circuit_space:
            if self.__instructions[position]:
                self.__remove_instruction(self.__instructions[position])
            self.__instruction_count += 1
            self.__instructions[position] = instruction
            instruction.use(position)
        else:
            # illegal position removes the instruction from the circuit if possible
            self.__remove_instruction(instruction)

    def __move_instruction(self, instruction: Instruction, position: int) -> bool:
        if instruction.is_used():
            if 0 <= position < self.__attributes.circuit_space:
                if self.__instructions[position]:
                    prev_pos = instruction.position
                    self.__remove_instruction(instruction, skip_qargs=True)
                    if GameplayConfig.auto_swap_gates():
                        self.__place_instruction(self.__instructions[position], prev_pos)
                    else:
                        self.__remove_instruction(self.__instructions[position])
                else:
                    self.__remove_instruction(instruction, skip_qargs=True)
                self.__place_instruction(instruction, position)
                return True
            else:
                self.__remove_instruction(instruction)
                return True
        return False

    def get_instruction(self, instruction_index: int) -> Instruction:
        if 0 <= instruction_index < self.backpack.used_capacity:
            return self.backpack.get(instruction_index)
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
            if self.is_space_left:
                self.__place_instruction(instruction, position)
            else:
                return False
        return self.__apply_instructions()

    def reset_circuit(self):
        temp = self.__instructions.copy()
        for instruction in temp:
            self.__remove_instruction(instruction)
        self.__instruction_count = 0
        self.__apply_instructions()
        self.update_statevector()

    def get_available_instructions(self) -> [Instruction]:
        """

        :return: a copy of all Instructions currently available to the robot
        """
        return self.backpack.copy_gates()

    def give_collectible(self, collectible: Collectible):
        if isinstance(collectible, Coin):
            self.backpack.give_coin(collectible.amount)
        elif isinstance(collectible, Key):
            self.backpack.give_key(collectible.amount)
        elif isinstance(collectible, Energy):
            self.__attributes.refill_energy(collectible.amount)
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
            Logger.instance().error(f"Received uncovered collectible: {collectible}")

    def on_move(self):
        _, died = self.__attributes.decrease_energy(amount=1)
        return died

    def damage(self, amount: int = 1) -> Tuple[int, bool]:
        return self.__attributes.damage(amount)

    def regenerate(self, amount: int = 1) -> int:
        """

        :param amount: how much energy to regenerate
        :return: how much was actually regenerated (e.g. cannot exceed max health)
        """
        return self.__attributes.refill_energy(amount)

    def get_circuit_print(self) -> str:
        entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
        rows = [[entry] * self.circuit_space for _ in range(self.num_of_qubits)]

        for i, inst in enumerate(self.__instructions):
            if inst:
                for q in inst.qargs_iter():
                    inst_str = inst.abbreviation(q)
                    diff_len = InstructionConfig.MAX_ABBREVIATION_LEN - len(inst_str)
                    inst_str = f"--{{{inst_str}}}--"
                    if diff_len > 0:
                        half_diff = int(diff_len / 2)
                        inst_str = inst_str.ljust(len(inst_str) + half_diff, "-")
                        if diff_len % 2 == 0:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff, "-")
                        else:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff + 1, "-")
                    rows[q][i] = inst_str

        circ_str = ""
        # place qubits from top to bottom, high to low index
        for q in range(len(rows) - 1, -1, -1):
            circ_str += f"| q{q} >---"
            row = rows[q]
            for i in range(len(row)):
                circ_str += row[i]
                if i < len(row) - 1:
                    circ_str += "+"
            circ_str += "< out |\n"
        return circ_str


class TestBot(Robot):
    def __init__(self, game_over_callback: Callable[[], None], num_of_qubits: int = 2, gates: List[Instruction] = None):
        attributes = _Attributes(DummyQubitSet(num_of_qubits))
        backpack = Backpack(5, gates)

        super(TestBot, self).__init__("Testbot", attributes, backpack, game_over_callback)
    
    def give_collectible(self, collectible: Collectible):
        super(TestBot, self).give_collectible(collectible)

    def get_img(self):
        return "T"

    def description(self) -> str:
        return "A Robot for testing, debugging etc."


class LukeBot(Robot):
    def __init__(self, game_over_callback: Callable[[], None], size: int = 2):
        attributes = _Attributes(DummyQubitSet(size))
        backpack = Backpack(capacity=5)

        # randomness is not allowed during Robot creation because it messes up the seed
        # add random gates and a HealthPotion
        #rm = RandomManager.create_new()
        #if rm.get(msg="LukeBot.init()") < 0.5:
        #    num_of_gates = 3
        #else:
        #    num_of_gates = 4
        #gate_factory = GateFactory.default()
        #for gate in gate_factory.produce_multiple(rm, num_of_gates):
        #    backpack.add(gate)
        #backpack.place_in_pouch(HealthPotion(3))
        super().__init__("Luke", attributes, backpack, game_over_callback)

    def get_img(self):
        return "L"

    def description(self) -> str:
        return "The loyal Robot you start with. A true all-rounder - take good care of it!"
