import enum
from abc import ABC, abstractmethod
from typing import Iterator, Optional, List

import qiskit.circuit
import qiskit.circuit.library.standard_gates as gates
from qiskit import QuantumCircuit

from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import ShopConfig, Logger
from qrogue.util.util_classes import RelationalGrid


class GateType(enum.Enum):
    # unique by their short name
    IGate = "I"
    XGate = "X"
    YGate = "Y"
    ZGate = "Z"
    HGate = "Hadamard"

    SwapGate = "Swap"
    CXGate = "CX"

    DummyGate = "dummy"

    def __init__(self, short_name: str):
        self.__short_name = short_name

    @property
    def short_name(self) -> str:
        return self.__short_name


class Instruction(Collectible, ABC):
    """
    Wrapper class for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
    """
    MAX_ABBREVIATION_LEN = 5
    __DEFAULT_PRICE = 15 * ShopConfig.base_unit()
    __GATE_DESCRIPTIONS = {
        # GateType -> "description"
        GateType.IGate: "An I Gate or Identity Gate doesn't alter the Qubit in any way. It can be used as a "
                        "placeholder.",
        GateType.XGate: "In the classical world an X Gate corresponds to an inverter. It swaps the amplitudes of |0> "
                        "and |1>.\nIn the quantum world this corresponds to a rotation of 180° along the x-axis, hence "
                        "the name X Gate.",
        GateType.YGate: "A Y Gate rotates the Qubit along the y-axis by 180°.",
        GateType.ZGate: "A Z Gate rotates the Qubit along the z-axis by 180°.",
        GateType.HGate: "The Hadamard Gate is often used to bring Qubits to Superposition. In a simple case this "
                        "corresponds to a rotation of 90°.",

        GateType.SwapGate: "As the name suggests, Swap Gates swap the amplitude between two Qubits.",
        GateType.CXGate: "Applies an X Gate onto its second Qubit if its first Qubit is 1.",
    }

    @staticmethod
    def get_description(gate_type: GateType) -> str:
        assert gate_type in Instruction.__GATE_DESCRIPTIONS, f"Invalid GateType: {gate_type}! No description available."
        return Instruction.__GATE_DESCRIPTIONS[gate_type]

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

    @property
    def all_qubits_specified(self) -> bool:
        return len(self._qargs) == self.num_of_qubits

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
        return not self.all_qubits_specified

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

    def qargs_copy(self) -> List[int]:
        return self._qargs.copy()

    def get_qubit_at(self, index: int = 0) -> int:
        if 0 <= index < len(self._qargs):
            return self._qargs[index]

    def name(self) -> str:
        return f"{self.__type.short_name} Gate"

    def description(self) -> str:
        return Instruction.get_description(self.__type)

    @abstractmethod
    def abbreviation(self, qubit: int = 0):
        pass

    @abstractmethod
    def copy(self, include_args: bool = False) -> "Instruction":
        """
        :param include_args: whether to also copy qargs and cargs
        """
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
        return self.to_string()


####### Single Qubit Gates #######


class SingleQubitGate(Instruction, ABC):
    def __init__(self, gate_type: GateType, instruction: qiskit.circuit.Gate):
        super().__init__(gate_type, instruction, needed_qubits=1)


class IGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.IGate, gates.IGate())

    def abbreviation(self, qubit: int = 0):
        return "I"

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = IGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class XGate(SingleQubitGate):
    def __init__(self):
        super(XGate, self).__init__(GateType.XGate, gates.XGate())

    def abbreviation(self, qubit: int = 0):
        return " X "

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = XGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class YGate(SingleQubitGate):
    def __init__(self):
        super(YGate, self).__init__(GateType.YGate, gates.YGate())

    def abbreviation(self, qubit: int = 0):
        return " Y "

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = YGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class ZGate(SingleQubitGate):
    def __init__(self):
        super(ZGate, self).__init__(GateType.ZGate, gates.ZGate())

    def abbreviation(self, qubit: int = 0):
        return " Z "

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = ZGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class HGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.HGate, gates.HGate())

    def abbreviation(self, qubit: int = 0):
        return " H "

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = HGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


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


class MultiQubitIdentity(MultiQubitGate):
    def __init__(self, needed_qubits: int):
        mqi_circuit = QuantumCircuit(needed_qubits, name='Is')
        mqi_circuit.i(range(needed_qubits))
        mqi_gate = mqi_circuit.to_gate()

        super().__init__(GateType.IGate, mqi_gate, needed_qubits)

    def _internal_abbreviation(self, index: int):
        return f" I{index}"

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = MultiQubitIdentity(self.num_of_qubits)
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


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

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = SwapGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class CXGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(GateType.CXGate, gates.CXGate())

    def _internal_abbreviation(self, index: int) -> str:
        if index == 0:
            return " C "
        elif index == 1:
            return " X "

    def copy(self, include_args: bool = False) -> "Instruction":
        gate = CXGate()
        if include_args:
            gate._qargs = self._qargs.copy()
            gate._cargs = self._cargs.copy()
        return gate


class RelationalGridInstruction(RelationalGrid.Item[Instruction]):
    @property
    def num_of_rows(self) -> int:
        return self.value.num_of_qubits

    def row_iter(self) -> Iterator[int]:
        return self.value.qargs_iter()

    def row_copy(self) -> List[int]:
        return self.value.qargs_copy()

    def reset(self, skip_rows: bool = False, skip_column: bool = False):
        self.value.reset(skip_qargs=skip_rows, skip_position=skip_column)

    def __str__(self):
        return str(self.value)
