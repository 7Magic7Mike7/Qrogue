from typing import List, Optional

from qiskit import Aer, execute, transpile, QuantumRegister, QuantumCircuit as QiskitCircuit
from qiskit.circuit import Gate

from qrogue.util import Config

if Config.using_new_qiskit():
    from qiskit.providers.basicaer import StatevectorSimulatorPy as StatevectorSimulator
else:
    from qiskit.providers.aer import StatevectorSimulator


class QuantumCircuit:
    @staticmethod
    def from_register(num_qubits: int) -> "QuantumCircuit":
        return QuantumCircuit(QiskitCircuit(QuantumRegister(num_qubits)))

    @staticmethod
    def from_bit_num(num_qubits: int, num_cbits: int = 0) -> "QuantumCircuit":
        return QuantumCircuit(QiskitCircuit(num_qubits, num_cbits))

    def __init__(self, circuit: QiskitCircuit):
        self.__circuit = circuit

    @property
    def circuit(self) -> QiskitCircuit:
        return self.__circuit

    def append(self, gate: Gate, qargs: List[int], cargs: List[int]):
        self.__circuit.append(gate, qargs, cargs)

    def to_gate(self, label: Optional[str] = None) -> Gate:
        return self.__circuit.to_gate(label=label)

    def copy(self, name: Optional[str] = None) -> "QuantumCircuit":
        return QuantumCircuit(self.__circuit.copy(name))

    def __str__(self) -> str:
        return str(self.__circuit)


class QuantumSimulator:
    def __init__(self):
        self.__simulator = StatevectorSimulator()

    def run(self, circuit: QuantumCircuit, do_transpile: bool = False) -> List[complex]:
        circuit: QiskitCircuit = circuit.circuit    # unwrap circuit

        if do_transpile:
            circuit = transpile(circuit, self.__simulator)

        # optionally use:   ddsim.JKQProvider().get_backend('statevector_simulator')?
        if Config.using_new_qiskit():
            # this signature doesn't take "shots=1"
            job = self.__simulator.run(circuit)
        else:
            # We only do 1 shot since we don't need any measurement but the StateVector
            job = self.__simulator.run(circuit, shots=1)

        return job.result().get_statevector()   # todo maybe pass circuit as experiment?


class UnitarySimulator:
    def __init__(self):
        self.__backend = Aer.get_backend('unitary_simulator')

    def execute(self, circuit: QuantumCircuit, decimals: int) -> List[List[complex]]:
        circuit: QiskitCircuit = circuit.circuit    # unwrap circuit

        job = execute(circuit, self.__backend)
        result = job.result()
        return result.get_unitary(circuit, decimals).data
