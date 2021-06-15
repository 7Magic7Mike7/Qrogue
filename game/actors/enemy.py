
from qubit import Qubit

class Enemy:
    def __init__(self, qubits: "list of Qubits"):
        self.__qubits = qubits

    def damage(self, index: int, value: int):
        if 0 <= index < len(self.__qubits):
            self.__qubits[index].damage(value)

    def __str__(self):
        string = "Enemy {"
        for q in self.__qubits:
            string += str(q) + "\t"
        string += " }"
        return string
