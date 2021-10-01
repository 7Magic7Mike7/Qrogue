from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from game.logic.instruction import HGate
from game.logic.qubit import StateVector
from util.my_random import RandomManager


class Difficulty:
    __SHOTS = 1

    def __init__(self, instruction_set: "list of Instructions", num_of_instructions: int):
        self.__instruction_set = instruction_set
        self.__num_of_instructions = num_of_instructions

    def create_statevector(self, num_of_qubits: int) -> StateVector:
        circuit = QuantumCircuit(num_of_qubits, num_of_qubits)
        rand = RandomManager.instance()
        qubits = [i for i in range(num_of_qubits)]
        cbits = [i for i in range(num_of_qubits)]

        for i in range(self.__num_of_instructions):
            instruction = rand.get_element(self.__instruction_set)
            inst_qubits = qubits.copy()
            inst_cbits = cbits.copy()
            for i in range(len(instruction.qargs)):
                qubit = rand.get_element(inst_qubits, remove=True)
                instruction.qargs[i] = qubit
            for i in range(len(instruction.cargs)):
                cubit = rand.get_element(inst_cbits, remove=True)
                instruction.cargs[i] = cubit

            instruction.append_to(circuit)
        simulator = StatevectorSimulator()
        compiled_circuit = transpile(circuit, simulator)
        # We only do 1 shot since we don't need any measurement but the StateVector
        job = simulator.run(compiled_circuit, shots=1)
        stv = StateVector(job.result().get_statevector())
        return stv


class DummyDifficulty(Difficulty):
    def __init__(self):
        super(DummyDifficulty, self).__init__([HGate(0), HGate(1)], 2)
