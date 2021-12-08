"""
Author: Artner Michael
13.06.2021
"""

from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import StatevectorSimulator

from game.collectibles.collectible import Collectible, CollectibleType
from game.collectibles.consumable import Consumable
from game.collectibles import consumable
from game.collectibles import pickup
from game.logic.instruction import Instruction
from game.logic import instruction as gates
from game.logic.qubit import QubitSet, EmptyQubitSet, DummyQubitSet, StateVector
# from jkq import ddsim
from util.config import CheatConfig, Config
from util.logger import Logger


class PlayerAttributes:
    """
    Is used as storage for a bunch of attributes of the player
    """

    def __init__(self, qubits: QubitSet = EmptyQubitSet(), space: int = 3):
        """

        :param qubits: the set of qubits the player is currently using
        :param space: how many instructions the player can put on their circuit
        """
        self.__space = space
        self.__qubits = qubits

    @property
    def num_of_qubits(self) -> int:
        return self.__qubits.size()

    @property
    def space(self) -> int:
        return self.__space

    @property
    def qubits(self) -> QubitSet:
        return self.__qubits


class Backpack:
    """
    Stores Instructions, Consumables and other Collectibles for the player to use.
    """
    __CAPACITY = 5      # how many Instructions the Backpack can hold at once
    __POUCH_SIZE = 5    # how many Consumables the Backpack can hold at once

    def __init__(self, capacity: int = __CAPACITY, content: "list of Instructions" = []):
        """

        :param capacity: how many Instructions can be stored in this Backpack
        :param content: initially stored Instructions
        """
        self.__capacity = capacity
        self.__storage = content
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

    def store_in_pouch(self, consumable: Consumable) -> bool:
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

    def copy(self) -> "Backpack":
        data = []
        for instruction in self.__storage:
            data.append(instruction.copy())
        return Backpack(self.__capacity, data)


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


class Player(ABC):
    def __init__(self, attributes: PlayerAttributes = PlayerAttributes(), backpack: Backpack = Backpack()):
        # initialize qubit stuff (rows)
        self.__simulator = StatevectorSimulator()#ddsim.JKQProvider().get_backend('statevector_simulator')
        self.__stv = None
        self.__attributes = attributes
        self.__backpack = backpack
        self.__qubit_indices = []
        for i in range(0, attributes.num_of_qubits):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        self.__next_col = 0

        # apply gates/instructions, create the circuit
        self.__circuit = None
        self.__instructions = []
        self.__apply_instructions()
        self.update_statevector()  # to initialize the statevector

    @property
    def backpack(self) -> Backpack:
        return self.__backpack

    @property
    def state_vector(self) -> StateVector:
        return self.__stv

    @property
    def key_count(self) -> int:
        return self.backpack.key_count

    def use_key(self) -> bool:
        return self.backpack.use_key()

    def circuit_enumerator(self):
        return enumerate(self.__instructions)

    def update_statevector(self) -> StateVector:
        """
        Compiles and simulates the current circuit and saves and returns the resulting StateVector
        :return: an updated StateVector corresponding to the current circuit
        """
        compiled_circuit = transpile(self.__circuit, self.__simulator)
        job = self.__simulator.run(compiled_circuit, shots=1)
        result = job.result()
        self.__stv = StateVector(result.get_statevector(self.__circuit))
        return self.__stv

    def get_instruction(self, instruction_index: int) -> Instruction:
        if 0 <= instruction_index < self.backpack.used_capacity:
            return self.backpack.get(instruction_index)
        return None

    def has_empty_circuit(self) -> bool:
        return self.__next_col == 0

    def is_space_left(self) -> bool:
        return self.__next_col < self.__attributes.space

    def use_instruction(self, instruction: Instruction) -> bool:
        """
        Tries to put the Instruction corresponding to the given index in the backpack into the player's circuit.
        If the Instruction is already in-use (put onto the circuit) it is removed instead.

        :param instruction: the Instruction we want to use
        :return: True if we were able to use the Instruction in our circuit
        """
        if instruction.is_used():
            self.__remove_instruction(instruction)
        else:
            if self.is_space_left():
                self.__append_instruction(instruction)
            else:
                return False
        return self.__apply_instructions()

    def remove_instruction(self, instruction_index: int) -> bool:
        if 0 <= instruction_index < self.backpack.used_capacity:
            instruction = self.backpack.get(instruction_index)
            self.__remove_instruction(instruction)
        return self.__apply_instructions()

    def reset_circuit(self):
        temp = self.__instructions.copy()
        for instruction in temp:
            self.__remove_instruction(instruction)
        self.__apply_instructions()
        self.update_statevector()

    def __append_instruction(self, instruction: Instruction):
        self.__instructions.append(instruction)
        instruction.use()
        self.__next_col += 1

    def __remove_instruction(self, instruction: Instruction):
        self.__instructions.remove(instruction)
        instruction.reset()
        self.__next_col -= 1

    def get_available_instructions(self) -> "list of Instructions":
        """

        :return: a copy of all Instructions currently available to the player
        """
        data = []
        bp = self.backpack.copy()
        for instruction in bp:
            data.append(instruction)
        return data

    def give_collectible(self, collectible: Collectible):
        if isinstance(collectible, pickup.Coin):
            self.backpack.give_coin(collectible.amount)
        elif isinstance(collectible, pickup.Key):
            self.backpack.give_key(collectible.amount)
        elif isinstance(collectible, pickup.Heart):
            self.heal(collectible.amount)
        elif isinstance(collectible, Instruction):
            self.backpack.add(collectible)
        elif collectible.type is CollectibleType.Consumable:
            self.backpack.store_in_pouch(collectible)

    def damage(self, target: StateVector = None, amount: int = 1) -> int:
        return self.__attributes.qubits.damage(amount)

    def heal(self, amount: int = 1) -> int:
        """

        :param amount: how much hp to heal
        :return: how much was actually healed (e.g. cannot exceed max health)
        """
        return self.__attributes.qubits.heal(amount)

    @property
    def cur_hp(self) -> int:
        return self.__attributes.qubits.hp()

    @property
    def num_of_qubits(self) -> int:
        return self.__attributes.num_of_qubits

    @property
    def space(self) -> int:
        return self.__attributes.space

    def __apply_instructions(self):
        circuit = QuantumCircuit(self.__attributes.num_of_qubits, self.__attributes.num_of_qubits)
        for inst in self.__instructions:
            inst.append_to(circuit)
        self.__circuit = circuit
        return True

    @staticmethod
    def __counts_to_bit_list(counts):
        counts = str(counts)
        counts = counts[1:len(counts)-1]
        arr = counts.split(':')
        if int(arr[1][1:]) != 1:
            Logger.instance().throw(ValueError(f"Function only works for counts with 1 shot but counts was: {counts}"))
        bits = arr[0]
        bits = bits[1:len(bits)-1]
        list = []
        for b in bits:
            list.append(int(b))
        list.reverse()   # so that list[i] corresponds to the measured value of qi
        return list


class DummyPlayer(Player):
    def __init__(self):
        attributes = PlayerAttributes(DummyQubitSet())
        backpack = Backpack(5, [gates.HGate(), gates.XGate()])
        backpack.store_in_pouch(consumable.HealthPotion(3))
        super(DummyPlayer, self).__init__(attributes, backpack)

    def get_img(self):
        return "P"
