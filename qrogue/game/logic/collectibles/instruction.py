import enum
from abc import ABC, abstractmethod
from typing import Iterator, Optional, Set, Dict

import math
import qiskit.circuit
import qiskit.circuit.library.standard_gates as gates
from qiskit import QuantumCircuit

from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import ShopConfig, Logger
from qrogue.util.util_functions import rad2deg


class GateType(enum.Enum):
    # unique by their short name
    IGate = "I", {"Identity"}, \
            "An I Gate or Identity Gate doesn't alter the Qubit in any way. It can be used as a placeholder."
    XGate = "X", {"Pauli X", "Pauli-X"}, \
            "In the classical world an X Gate corresponds to an inverter. It swaps the amplitudes of |0> and |1>.\n" \
            "In the quantum world this corresponds to a rotation of 180° along the x-axis, hence the name X Gate."
    YGate = "Y", {"Pauli Y", "Pauli-Y"}, \
            "A Y Gate rotates the Qubit along the y-axis by 180°."
    ZGate = "Z", {"Pauli Z", "Pauli-Z"}, \
            "A Z Gate rotates the Qubit along the z-axis by 180°."
    HGate = "H", {"Hadamard"}, \
            "The Hadamard Gate is often used to bring Qubits to Superposition. In a simple case (i.e., phase is 0) " \
            "this corresponds to a rotation of 90° along the x-axis."

    SGate = "S", {"Phase", "P"}, \
            "The S Gate can change the phase of a qubit by multiplying its |1> with i. It is equivalent to a " \
            "rotation along the z-axis by 90°."
    RYGate = "RY", {"Rotational Y", "Rot Y"}, \
             "The RY Gate conducts a rotation along the y-axis by a certain angle. In our case the angle is 90°."
    RZGate = "RZ", {"Rotational Z", "Rot Z"}, \
             "The RZ Gate conducts a rotation along the z-axis by a certain angle. In our case the angle is 90°."

    SwapGate = "Swap", set(), \
               "As the name suggests, Swap Gates swap the amplitude between two Qubits."
    CXGate = "CX", {"Controlled X", "CNOT", "Controlled NOT"}, \
             "Applies an X Gate onto its second Qubit if its first Qubit is 1."

    def __init__(self, short_name: str, other_names: Set[str], description: str):
        self.__short_name = short_name
        self.__names = other_names
        self.__names.add(short_name)
        self.__description = description

    @property
    def short_name(self) -> str:
        return self.__short_name

    @property
    def description(self) -> str:
        return self.__description

    def is_in_names(self, name: str) -> bool:
        if name in self.__names:
            return True
        name = name.lower()
        for n in self.__names:
            if name == n.lower():
                return True
        return False


class Instruction(Collectible, ABC):
    """
    Wrapper class for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
    """
    MAX_ABBREVIATION_LEN = 5
    __DEFAULT_PRICE = 15 * ShopConfig.base_unit()

    def __init__(self, gate_type: GateType, instruction: qiskit.circuit.Gate, needed_qubits: int):
        super().__init__(CollectibleType.Gate)
        self.__type = gate_type
        self.__instruction = instruction
        self.__needed_qubits = needed_qubits
        self._qargs = []
        self._cargs = []
        self.__position: Optional[int] = None

    @property
    def gate_type(self) -> GateType:
        return self.__type

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
        return f"{self.__type.short_name} Gate"

    def description(self) -> str:
        return self.__type.description

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
        text = f"{self.__type.name} ("
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
        text = self.to_string()
        if self.__position is not None: text += f" [pos={self.__position}]"
        if len(self._qargs) > 0: text += f" @q{self._qargs[0]}"
        for i in range(1, len(self._qargs)): text += f", {self._qargs[i]}"
        return text


####### Single Qubit Gates #######


class SingleQubitGate(Instruction, ABC):
    def __init__(self, gate_type: GateType, instruction: qiskit.circuit.Gate):
        super().__init__(gate_type, instruction, needed_qubits=1)


class IGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.IGate, gates.IGate())

    def abbreviation(self, qubit: int = 0):
        return "I"

    def copy(self) -> "Instruction":
        return IGate()


class XGate(SingleQubitGate):
    def __init__(self):
        super(XGate, self).__init__(GateType.XGate, gates.XGate())

    def abbreviation(self, qubit: int = 0):
        return " X "

    def copy(self) -> "Instruction":
        return XGate()


class YGate(SingleQubitGate):
    def __init__(self):
        super(YGate, self).__init__(GateType.YGate, gates.YGate())

    def abbreviation(self, qubit: int = 0):
        return " Y "

    def copy(self) -> "Instruction":
        return YGate()


class ZGate(SingleQubitGate):
    def __init__(self):
        super(ZGate, self).__init__(GateType.ZGate, gates.ZGate())

    def abbreviation(self, qubit: int = 0):
        return " Z "

    def copy(self) -> "Instruction":
        return ZGate()


class HGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.HGate, gates.HGate())

    def abbreviation(self, qubit: int = 0):
        return " H "

    def copy(self) -> "Instruction":
        return HGate()


class SGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.SGate, gates.SGate())

    def abbreviation(self, qubit: int = 0):
        return " S "

    def copy(self) -> "Instruction":
        return SGate()


class RotationGate(SingleQubitGate, ABC):
    _DEFAULT_ANGLE = math.pi / 2

    def __init__(self, gate_type: GateType, instruction: qiskit.circuit.Gate, angle: float):
        super().__init__(gate_type, instruction)
        self.__angle = angle

    @property
    def angle(self) -> float:
        return self.__angle

    def description(self) -> str:
        desc = super().description()   # remove the stated default angle at the end
        # find indices of "°" and the whitespace before that, so we can replace the angle value.
        degree_index = desc.find("°")
        if degree_index <= 0:
            Logger.instance().error(f"No \"°\" in the description of {self.type}!")
            return desc
        space_index = desc[:degree_index].rfind(" ")

        # round and skip potential ".00"s
        angle = str(round(rad2deg(self.angle), 2))
        if angle.endswith(".00"): angle = angle[:-3]

        return f"{desc[:space_index]} {angle}{desc[degree_index:]}"


class RYGate(RotationGate):
    def __init__(self, angle: float = RotationGate._DEFAULT_ANGLE):
        super().__init__(GateType.RYGate, gates.RYGate(theta=angle), angle)

    def abbreviation(self, qubit: int = 0):
        return " RY"

    def copy(self) -> "Instruction":
        return RYGate(self.angle)


class RZGate(RotationGate):
    def __init__(self, angle: float = RotationGate._DEFAULT_ANGLE):
        super().__init__(GateType.RZGate, gates.RZGate(phi=angle), angle)

    def abbreviation(self, qubit: int = 0):
        return " RZ"

    def copy(self) -> "Instruction":
        return RZGate(self.angle)


####### Multi Qubit Gates ########


class MultiQubitGate(Instruction, ABC):
    def abbreviation(self, qubit: int = 0):
        if qubit in self._qargs:
            index = self._qargs.index(qubit)
        else:
            # during placement, we need an abbreviation for the next qubit
            index = len(self._qargs)
        return self._internal_abbreviation(index)

    @abstractmethod
    def _internal_abbreviation(self, index: int):
        pass


####### Double Qubit Gates #######


class DoubleQubitGate(MultiQubitGate, ABC):
    def __init__(self, gate_type: GateType, instruction: qiskit.circuit.Gate):
        super(DoubleQubitGate, self).__init__(gate_type, instruction, needed_qubits=2)


class SwapGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(GateType.SwapGate, gates.SwapGate())

    def _internal_abbreviation(self, index: int) -> str:
        if index == 0:
            return " S0"
        elif index == 1:
            return " S1"

    def copy(self) -> "Instruction":
        return SwapGate()


class CXGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(GateType.CXGate, gates.CXGate())

    def _internal_abbreviation(self, index: int) -> str:
        if index == 0:
            return " C "
        elif index == 1:
            return " X "

    def copy(self) -> "Instruction":
        return CXGate()


class InstructionManager:
    __GATES: Dict[GateType, Instruction] = {
        GateType.IGate: IGate(),

        GateType.XGate: XGate(),
        GateType.YGate: YGate(),
        GateType.ZGate: ZGate(),

        GateType.HGate: HGate(),
        GateType.SGate: SGate(),

        GateType.RYGate: RYGate(),
        GateType.RZGate: RZGate(),

        GateType.SwapGate: SwapGate(),
        GateType.CXGate: CXGate(),
    }

    @staticmethod
    def from_name(name: str) -> Optional[Instruction]:
        for val in GateType:
            if val.is_in_names(name):
                return InstructionManager.__GATES[val]
        return None
