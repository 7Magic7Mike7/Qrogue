"""
Author: Artner Michael
13.06.2021
"""

from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import AerSimulator
from game.logic.qubit import Qubit
from game.logic.instruction import Instruction


class PlayerAttributes:
    # default values
    NUM_OF_QUBITS = 2
    NUM_OF_COLS = 3
    ZERO_LIFE = 4
    ONE_LIFE = 4

    def __init__(self):
        self.__num_of_qubits = self.NUM_OF_QUBITS
        self.__num_of_cols = self.NUM_OF_COLS
        self.__init_qubits()

    def __init_qubits(self):
        self.__qubits = []
        for i in range(self.__num_of_qubits):
            self.__qubits.append(Qubit(i, zero_life=self.ZERO_LIFE, one_life=self.ONE_LIFE))

    def get_num_of_qubits(self):
        return self.__num_of_qubits

    def set_num_of_qubits(self, value: int):
        if value < 1:
            raise ValueError("value must be >= 1!")
        self.__num_of_qubits = value
        self.__init_qubits()

    def get_num_of_cols(self):
        return self.__num_of_cols

    def set_num_of_cols(self, value: int):
        if value < 1:
            raise ValueError("value must be >= 1!")
        self.__num_of_cols = value

    def get_qubits(self):
        return self.__qubits

    def set_qubit_life(self, qubit: int, zero_life: int = 0, one_life: int = 0):
        if qubit < 0 or self.__num_of_qubits <= qubit:
            raise ValueError(f"Invalid qubit: 0 <= {qubit} < {self.__num_of_qubits} not given!")
        if zero_life <= 0:
            zero_life = self.__qubits[qubit].get_zero_life()
        if one_life <= 0:
            one_life = self.__qubits[qubit].get_one_life()
        self.__qubits[qubit] = Qubit(qubit, zero_life, one_life)


class Player:
    def __init__(self, attributes: PlayerAttributes = PlayerAttributes()):
        # initialize qubit stuff (rows)
        self.__attributes = attributes
        self.__qubit_indices = []
        for i in range(0, attributes.get_num_of_qubits()):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        #self.num_of_cols = num_of_cols
        self.next_col = 0

        # apply gates/instructions, create the circuit
        self.set_generator()
        self.circuit = None
        self.instructions = []
        self.__apply_instructions()

    def set_generator(self, instructions: "list of Instructions" = None):
        num = self.__attributes.get_num_of_qubits()
        self.generator = QuantumCircuit(num, num)
        if instructions is None:        # default generator
            for i in range(num):
                self.generator.h(i)     # HGate on every qubit
        else:
            for inst in instructions:
                self.generator.append(inst.instruction, qargs=inst.qargs, cargs=inst.cargs)

    def measure(self):
        result = self.__get_result(self.circuit)
        counts = result.get_counts(self.circuit)
        return self.__counts_to_bit_list(counts)

    def use_instruction(self, instruction: Instruction):
        if self.next_col < self.__attributes.get_num_of_cols():
            self.instructions.append(instruction)
            self.next_col += 1
        else:
            print("Error, no more space available")
        self.__apply_instructions()
        return True

    def print(self):
        for qubit in self.__attributes.get_qubits():
            print(qubit)
        print(self.circuit)
        #self.circuit.draw(output="mpl")
        #plt.show()

    def defend(self, input):    # TODO input should be the generator output of the enemy
        num = self.__attributes.get_num_of_qubits()
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
        qubits = self.__attributes.get_qubits()
        for i in range(len(bit_list)):
            qubits[i].damage(bit_list[i])
        return bit_list

    def get_num_of_qubits(self):
        return self.__attributes.get_num_of_qubits()

    def __get_result(self, circuit: QuantumCircuit, shots: int = 1):
        simulator = AerSimulator()
        compiled_circuit = transpile(circuit, simulator)
        job = simulator.run(compiled_circuit, shots=shots)
        return job.result()

    def __apply_instructions(self):
        circuit = self.generator.copy(name="PlayerCircuit")
        for inst in self.instructions:
            circuit.append(inst.instruction, qargs=inst.qargs, cargs=inst.cargs)
        circuit.measure(self.__qubit_indices, self.__qubit_indices)
        self.circuit = circuit

    def __counts_to_bit_list(self, counts):
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


