"""
Author: Artner Michael
13.06.2021
"""

from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import StatevectorSimulator

from game.logic.instruction import Instruction, HGate
from game.logic.qubit import QubitSet, EmptyQubitSet, DummyQubitSet, StateVector
# from jkq import ddsim


class PlayerAttributes:
    # default values
    __CIRCUIT_SPACE = 3

    def __init__(self, qubits: QubitSet = EmptyQubitSet(), space: int = __CIRCUIT_SPACE):
        self.__space = space
        self.__qubits = qubits

    @property
    def num_of_qubits(self):
        return self.__qubits.size()

    @property
    def space(self):
        return self.__space

    def set_space(self, value: int):
        if value < 1:
            raise ValueError("value must be >= 1!")
        self.__space = value

    @property
    def qubits(self):
        return self.__qubits


class Backpack:
    CAPACITY = 4

    def __init__(self, capacity: int = CAPACITY, content: "list of Instructions" = []):
        self.__capacity = capacity
        self.__storage = content

    @property
    def capacity(self):
        return self.__capacity

    @property
    def size(self):
        return len(self.__storage)

    def get(self, index: int):
        if 0 <= index < self.size:
            return self.__storage[index]

    def add(self, instruction: Instruction):
        if len(self.__storage) < self.__capacity:
            self.__storage.append(instruction)
            return True
        return False

    def remove(self, instruction: Instruction):
        for i in range(len(self.__storage)):
            if self.__storage[i] == instruction:
                self.__storage.remove(instruction)
                return True
        return False


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
        self.next_col = 0

        # apply gates/instructions, create the circuit
        self.generator = None
        self.set_generator()
        self.circuit = None
        self.instructions = []
        self.__apply_instructions()

    @property
    def backpack(self):
        return self.__backpack

    @property
    def state_vector(self):
        return self.__stv

    def set_generator(self, instructions: "list of Instructions" = None):
        num = self.__attributes.num_of_qubits
        if num > 0:
            self.generator = QuantumCircuit(num, num)
            if instructions is None:        # default generator
                for i in range(num):
                    self.generator.h(i)     # HGate on every qubit
            else:
                for inst in instructions:
                    self.generator.append(inst.instruction, qargs=inst.qargs, cargs=inst.cargs)

    def measure(self) -> StateVector:
        result = self.__get_result(self.circuit)
        self.__stv = StateVector(result.get_statevector(self.circuit))
        return self.__stv
        #counts = result.get_counts(self.circuit)
        #return self.__counts_to_bit_list(counts)

    def use_instruction(self, instruction_index: int):
        if 0 <= instruction_index < self.__backpack.size:
            instruction = self.__backpack.get(instruction_index)
            if self.next_col < self.__attributes.space:
                self.instructions.append(instruction)
                self.next_col += 1
            else:
                print("Error, no more space available") # TODO use logger or popup?
            return self.__apply_instructions()
        return False

    def remove_instruction(self, column: int):
        if self.next_col == 0:
            return
        if 0 <= column < len(self.instructions):
            self.instructions.remove(self.instructions[column])
            self.next_col = self.next_col-1

    def print(self):
        print(self.circuit)
        #self.circuit.draw(output="mpl")
        #plt.show()

    def defend(self, input):
        """"
        num = self.__attributes.num_of_qubits
        reversed_circuit = QuantumCircuit(num, num)
        for i in range(self.next_col):
            index = self.next_col-1 - i
            if self.instructions[index]: # check if the instruction at this column uses the qubit q
                rev_inst = self.instructions[index]
                reversed_circuit.append(rev_inst.instruction.reverse_ops(), qargs=rev_inst.qargs, cargs=rev_inst.cargs)

        for q in range(num):
            reversed_circuit.measure(self.__qubit_indices, self.__qubit_indices)

        result = self.__get_result(reversed_circuit)
        counts = result.get_counts(reversed_circuit)
        bit_list = self.__counts_to_bit_list(counts)
        self.__attributes.qubits.damage(bit_list.count(0), bit_list.count(1))
        return bit_list
        """
        raise DeprecationWarning(self.defend)

    def get_qubit_string(self, index: int):
        if 0 <= index < self.num_of_qubits:
            return f"q_{index}"
        else:
            return "ERROR"  # todo adapt?

    @property
    def num_of_qubits(self):
        return self.__attributes.num_of_qubits

    def __get_result(self, circuit: QuantumCircuit, shots: int = 1):
        compiled_circuit = transpile(circuit, self.__simulator)
        job = self.__simulator.run(compiled_circuit, shots=shots)
        return job.result()

    def __apply_instructions(self):
        if self.generator is None:
            return False
        circuit = self.generator.copy(name="PlayerCircuit")
        for inst in self.instructions:
            inst.append_to(circuit)
        self.circuit = circuit
        return True

    @staticmethod
    def __counts_to_bit_list(counts):
        counts = str(counts)
        counts = counts[1:len(counts)-1]
        arr = counts.split(':')
        if int(arr[1][1:]) != 1:
            raise ValueError(f"Function only works for counts with 1 shot but counts was: {counts}")
        bits = arr[0]
        bits = bits[1:len(bits)-1]
        list = []
        for b in bits:
            list.append(int(b))
        list.reverse()   # so that list[i] corresponds to the measured value of qi
        return list


class DummyPlayer(Player):
    __ATTR = PlayerAttributes(DummyQubitSet())
    __BACKPACK = Backpack(3, [HGate(0), HGate(1), HGate(2)])

    def __init__(self):
        super(DummyPlayer, self).__init__(attributes=self.__ATTR, backpack=self.__BACKPACK)

    def get_img(self):
        return "P"