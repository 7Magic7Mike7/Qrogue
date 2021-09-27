
from abc import ABC, abstractmethod

import qiskit.circuit.library.standard_gates as gates


# wrapper for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
from qiskit import QuantumCircuit


class Instruction(ABC):
    def __init__(self, instruction, qargs: "list of ints", cargs: "list of ints" = None):
        self.__instruction = instruction
        self.__qargs = qargs
        if cargs is None:
            self.__cargs = []
        else:
            self.__cargs = cargs

    def append_to(self, circuit: QuantumCircuit):
        circuit.append(self.__instruction, self.__qargs, self.__cargs)

    @property
    def instruction(self):
        return self.__instruction

    @property
    def qargs(self) -> "list of ints":
        return self.__qargs

    @property
    def cargs(self):
        return self.__cargs

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def abbreviation(self, qubit: int = 0):
        pass

    def __str__(self):
        return f"{self.name()} ({self.qargs}, {self.cargs})"


class HGate(Instruction):
    def __init__(self, qubit: int):
        super().__init__(gates.HGate(), qargs=[qubit])

    def name(self):
        return "HGate"

    def abbreviation(self, qubit: int = 0):
        return " H "


class SwapGate(Instruction):
    def __init__(self, q0: int, q1: int):
        super().__init__(gates.SwapGate(), qargs=[q0, q1])
        self.__q0 = q0
        self.__q1 = q1

    def name(self):
        return "Swap"

    def abbreviation(self, qubit: int = 0):
        if qubit == self.__q0:
            return " S0 "
        else:
            return " S1 "
