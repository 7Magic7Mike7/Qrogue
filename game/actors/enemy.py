
from game.logic.qubit import Qubit

class Enemy:
    def __init__(self, qubits: "list of Qubits"):
        self.__qubits = qubits

    @property
    def num_of_qubits(self):
        return len(self.__qubits)

    def damage(self, index: int, value: int, dmg: int = 1):
        if 0 <= index < len(self.__qubits):
            self.__qubits[index].damage(value, dmg)

    def is_alive(self): # at least one qubit must be still alive
        for qubit in self.__qubits:
            if qubit.is_alive():
                return True
        return False

    def get_qubit_string(self, index: int):
        if 0 <= index < len(self.__qubits):
            return self.__qubits[index].__str__()
        else:
            return "ERROR"  # todo adapt?

    def __str__(self):
        string = "Enemy {"
        for q in self.__qubits:
            string += str(q) + "\t"
        string += " }"
        return string
