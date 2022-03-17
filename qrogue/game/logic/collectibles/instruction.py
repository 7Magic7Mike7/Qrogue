
from abc import ABC, abstractmethod

import qiskit.circuit.library.standard_gates as gates
from qiskit import QuantumCircuit

from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import ShopConfig


class Instruction(Collectible, ABC):
    """
    Wrapper class for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
    """
    MAX_ABBREVIATION_LEN = 5
    __DEFAULT_PRICE = 15 * ShopConfig.base_unit()

    def __init__(self, instruction, needed_qubits: int):
        super().__init__(CollectibleType.Gate)
        self.__instruction = instruction
        self.__needed_qubits = needed_qubits
        self._qargs = []
        self._cargs = []
        self.__position = -1

    @property
    def num_of_qubits(self) -> int:
        return self.__needed_qubits

    @property
    def position(self) -> int:
        return self.__position

    def use_qubit(self, qubit: int) -> bool:
        """

        :param qubit: the qubit to use for this Instruction
        :return: True if more qubits are needed for the Instruction to work, False if there are enough
        """
        if len(self._qargs) >= self.__needed_qubits:
            return False
        self._qargs.append(qubit)
        return len(self._qargs) < self.__needed_qubits

    def is_used(self) -> bool:
        return self.__position >= 0

    def use(self, position: int):
        self.__position = position

    def reset(self, skip_qargs: bool = False, skip_position: bool = False):
        if not skip_qargs:
            self._qargs = []
        if not skip_position:
            self.__position = -1

    def append_to(self, circuit: QuantumCircuit):
        circuit.append(self.__instruction, self._qargs, self._cargs)

    def qargs_iter(self) -> "Iterator":
        return iter(self._qargs)

    def name(self) -> str:
        return self.short_name() + " Gate"

    @abstractmethod
    def short_name(self) -> str:
        pass

    @abstractmethod
    def abbreviation(self, qubit: int = 0):
        pass

    @abstractmethod
    def copy(self) -> "Instruction":
        pass

    def default_price(self) -> int:
        return Instruction.__DEFAULT_PRICE

    def selection_str(self) -> str:
        # Gate (qX, qY, ?, ...)
        text = f"{self.short_name()} ("
        for i in range(self.num_of_qubits - 1):
            if i < len(self._qargs):
                text += f"q{self._qargs[i]}, "
            else:
                text += "?, "
        if self.num_of_qubits - 1 < len(self._qargs):
            text += f"q{self._qargs[self.num_of_qubits - 1]})"
        else:
            text += "?)"
        if self.is_used():
            text += f" @{self.__position}"
        return text

    def preview_str(self, next_qubit: int) -> str:
        # Gate (qX, qY, ?, ...)
        self._qargs.append(next_qubit)  # pretend that we already set the next qubit
        preview = self.selection_str()
        self._qargs.pop()   # undo setting the next qubit because we only wanted to pretend that we did
        return preview

    def to_string(self):
        return self.name()

    def __str__(self) -> str:
        return self.to_string()


####### Single Qubit Gates #######


class SingleQubitGate(Instruction, ABC):
    def __init__(self, instruction):
        super().__init__(instruction, needed_qubits=1)


class IGate(SingleQubitGate):
    def __init__(self):
        super().__init__(gates.IGate())

    def short_name(self) -> str:
        return "I"

    def abbreviation(self, qubit: int = 0):
        return "I"

    def description(self) -> str:
        return "An I Gate or Identity Gate doesn't alter the Qubit in any way. It can be used as a placeholder."


class XGate(SingleQubitGate):
    def __init__(self):
        super(XGate, self).__init__(gates.XGate())

    def short_name(self) -> str:
        return "X"

    def abbreviation(self, qubit: int = 0):
        return " X "

    def description(self) -> str:
        return "An X Gate rotates the Qubit along the x-axis. This defines a swap of the amplitudes of |0> and |1> - " \
               "in the classical world this would describe an Inverter."

    def copy(self) -> "Instruction":
        return XGate()


class YGate(SingleQubitGate):
    def __init__(self):
        super(YGate, self).__init__(gates.YGate())

    def short_name(self) -> str:
        return "Y"

    def abbreviation(self, qubit: int = 0):
        return " Y "

    def description(self) -> str:
        return "A Y Gate rotates the Qubit along the y-axis by 180."

    def copy(self) -> "Instruction":
        return YGate()


class ZGate(SingleQubitGate):
    def __init__(self):
        super(ZGate, self).__init__(gates.ZGate())

    def short_name(self) -> str:
        return "Z"

    def abbreviation(self, qubit: int = 0):
        return " Z "

    def description(self) -> str:
        return "A Z Gate rotates the Qubit along the z-axis by 180°."

    def copy(self) -> "Instruction":
        return ZGate()


class HGate(SingleQubitGate):
    def __init__(self):
        super().__init__(gates.HGate())

    def description(self) -> str:
        return "The Hadamard Gate is often used to bring Qubits to Superposition."

    def short_name(self) -> str:
        return "Hadamard"

    def abbreviation(self, qubit: int = 0):
        return " H "

    def copy(self) -> "Instruction":
        return HGate()


####### Double Qubit Gates #######


class DoubleQubitGate(Instruction, ABC):
    def __init__(self, instruction):
        super(DoubleQubitGate, self).__init__(instruction, needed_qubits=2)


class SwapGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(gates.SwapGate())

    def description(self) -> str:
        return "As the name suggests, Swap Gates swap the amplitude between two Qubits."

    def short_name(self) -> str:
        return "Swap"

    def abbreviation(self, qubit: int = 0):
        if qubit == self._qargs[0]:
            return " S0 "
        else:
            return " S1 "

    def copy(self) -> "Instruction":
        return SwapGate()


class CXGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(gates.CXGate())

    def short_name(self) -> str:
        return "CX"

    def abbreviation(self, qubit: int = 0):
        if qubit == self._qargs[0]:
            return " C "
        else:
            return " X "

    def copy(self) -> "Instruction":
        return CXGate()

    def description(self) -> str:
        return f"Applies an X Gate onto its second Qubit if its first Qubit is True."
