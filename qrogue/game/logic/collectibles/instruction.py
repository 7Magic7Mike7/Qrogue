
from abc import ABC, abstractmethod
from typing import Iterator, Optional

import qiskit.circuit.library.standard_gates as gates
from qiskit import QuantumCircuit

from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import ShopConfig, Logger


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
        self.__position: Optional[int] = None

    @property
    def num_of_qubits(self) -> int:
        return self.__needed_qubits

    @property
    def position(self) -> Optional[int]:
        return self.__position

    @property
    def no_qubits_specified(self) -> bool:
        return len(self._qargs) <= 0

    def can_use_qubit(self, qubit: int) -> bool:
        return qubit not in self._qargs

    def use_qubit(self, qubit: int) -> bool:
        """

        :param qubit: the qubit to use for this Instruction
        :return: True if more qubits are needed for the Instruction to work, False if there are enough
        """
        if len(self._qargs) >= self.__needed_qubits:
            return False
        if not self.can_use_qubit(qubit):
            Logger.instance().error("Cannot use the same qubit multiple times!", from_pycui=False)
            return True
        self._qargs.append(qubit)
        return len(self._qargs) < self.__needed_qubits

    def is_used(self) -> bool:
        return self.__position is not None

    def use(self, position: int) -> bool:
        """
        Checks if this Instruction has all its needed information (e.g. qubit arguments) specified and then saves the
        given position.
        :param position: position where we want to use this Instruction at
        :return: True if this Instruction was successfully used/positioned, False otherwise
        """
        assert position >= 0

        if len(self._qargs) == self.__needed_qubits:
            self.__position = position
            return True
        return False

    def reset(self, skip_qargs: bool = False, skip_position: bool = False):
        if not skip_qargs:
            self._qargs = []
        if not skip_position:
            self.__position = None

    def append_to(self, circuit: QuantumCircuit):
        circuit.append(self.__instruction, self._qargs, self._cargs)

    def qargs_iter(self) -> Iterator[int]:
        return iter(self._qargs)

    def get_qubit_at(self, index: int = 0) -> int:
        if 0 <= index < len(self._qargs):
            return self._qargs[index]

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

    def copy(self) -> "Instruction":
        return IGate()


class XGate(SingleQubitGate):
    def __init__(self):
        super(XGate, self).__init__(gates.XGate())

    def short_name(self) -> str:
        return "X"

    def abbreviation(self, qubit: int = 0):
        return " X "

    def description(self) -> str:
        return "In the classical world an X Gate corresponds to an inverter. It swaps the amplitudes of |0> and |1>, " \
               "hence describing a 180° rotation along the x-axis."

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


####### Multi Qubit Gates ########


class MultiQubitGate(Instruction, ABC):
    def abbreviation(self, qubit: int = 0):
        if qubit in self._qargs:
            index = self._qargs.index(qubit)
        else:
            # during placement we need an abbreviation for the next qubit
            index = len(self._qargs)
        return self._internal_abbreviation(index)

    @abstractmethod
    def _internal_abbreviation(self, index: int):
        pass


####### Double Qubit Gates #######


class DoubleQubitGate(MultiQubitGate, ABC):
    def __init__(self, instruction):
        super(DoubleQubitGate, self).__init__(instruction, needed_qubits=2)


class SwapGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(gates.SwapGate())

    def description(self) -> str:
        return "As the name suggests, Swap Gates swap the amplitude between two Qubits."

    def short_name(self) -> str:
        return "Swap"

    def _internal_abbreviation(self, index: int):
        return [" S1 ", " S0 "][index]

    def copy(self) -> "Instruction":
        return SwapGate()


class CXGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(gates.CXGate())

    def short_name(self) -> str:
        return "CX"

    def _internal_abbreviation(self, index: int):
        return [" C ", " X "][index]

    def copy(self) -> "Instruction":
        return CXGate()

    def description(self) -> str:
        return f"Applies an X Gate onto its second Qubit if its first Qubit is 1."
