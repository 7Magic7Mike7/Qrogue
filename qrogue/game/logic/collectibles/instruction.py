import enum
import math
from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, List, Callable, Tuple

import qiskit.circuit.library.standard_gates as gates
from qiskit.circuit import Gate as QiskitGate

from qrogue.game.logic.base import StateVector, CircuitMatrix, QuantumSimulator, QuantumCircuit, UnitarySimulator
from qrogue.game.logic.collectibles import Collectible, CollectibleType
from qrogue.util import Logger, GateType, QuantumSimulationConfig, InstructionConfig, ColorConfig, ColorCode
from qrogue.util.achievements import Unlocks
from qrogue.util.util_functions import rad2deg, center_string, to_binary_string


class Instruction(Collectible, ABC):
    """
    Wrapper class for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
    """
    MAX_ABBREVIATION_LEN = 5

    @staticmethod
    def compute_stv(instructions: List["Instruction"], num_of_qubits: int, inverse: bool = False) -> StateVector:
        circuit = QuantumCircuit.from_bit_num(num_of_qubits, num_of_qubits)
        for instruction in instructions:
            instruction.append_to(circuit, inverse)
        simulator = QuantumSimulator()
        amplitudes = simulator.run(circuit, do_transpile=True)
        return StateVector(amplitudes, num_of_used_gates=len(instructions))

    @staticmethod
    def __circuit_input_value(qubit: int, state_vectors: Optional[Tuple[StateVector, StateVector, StateVector]]):
        if state_vectors is not None:
            input_stv, output_stv, target_stv = state_vectors
            if input_stv is not None and input_stv.is_classical \
                    and target_stv is not None and target_stv.is_classical \
                    and output_stv.is_classical:  # robot.state_vector cannot be None
                index = input_stv.to_value().index(1)  # find where the amplitude is 1
                # get the respective qubit values but in lsb, so we can use $qubit directly as index
                values = to_binary_string(index, input_stv.num_of_qubits, msb=False)
                return f"= {values[qubit]} "
        return ""

    @staticmethod
    def __circuit_output_value(qubit: int, state_vectors: Optional[Tuple[StateVector, StateVector, StateVector]]) -> str:
        if state_vectors is not None:
            input_stv, output_stv, target_stv = state_vectors
            if input_stv is not None and input_stv.is_classical \
                    and target_stv is not None and target_stv.is_classical \
                    and output_stv.is_classical:  # robot.state_vector cannot be None
                index = output_stv.to_value().index(1)  # find where the amplitude is 1
                # get the respective qubit values but in lsb, so we can use $qubit directly as index
                out_values = to_binary_string(index, output_stv.num_of_qubits, msb=False)
                index = target_stv.to_value().index(1)
                target_values = to_binary_string(index, target_stv.num_of_qubits, msb=False)
                is_correct = out_values[qubit] == target_values[qubit]
                equality = ColorConfig.colorize(ColorCode.PUZZLE_CORRECT_AMPLITUDE if is_correct
                                                else ColorCode.PUZZLE_WRONG_AMPLITUDE,
                                                '=' + ('=' if is_correct else '/') + '=')
                return f"= {out_values[qubit]}| {equality} <{target_values[qubit]}|"
        return "|"

    @staticmethod
    def circuit_to_string(num_of_qubits: int, circuit_space: int, instructions: Dict[int, "Instruction"],
                          preview: Optional[Tuple[Optional["Instruction"], int, int]] = None,
                          state_vectors: Optional[Tuple[StateVector, StateVector, StateVector]] = None) -> str:
        """
        :param num_of_qubits: how many rows (i.e., qubits) the circuit has
        :param circuit_space: how many columns (i.e., places for instructions)
        :param instructions: all positions within the circuit where an Instruction is placed
        :param preview: optionally describes a gate that is not yet placed onto the circuit
        :param state_vectors: a tuple consisting of an Input-, Output- and Target-StateVector to potentially show a
            qubit's (classical) value
        :return: a string representing the described circuit
        """
        entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
        rows = [[entry] * circuit_space for _ in range(num_of_qubits)]
        for i, inst in instructions.items():
            for q in inst.qargs_iter():
                inst_str = center_string(inst.abbreviation(q), InstructionConfig.MAX_ABBREVIATION_LEN)
                rows[q][i] = f"--{{{inst_str}}}--"

        if preview is not None:
            inst, pos, qubit = preview
            if inst is None:
                rows[qubit][pos] = "--/   /--"
            else:
                for q in inst.qargs_iter():
                    rows[q][pos] = f"--{{{inst.abbreviation(q)}}}--"
                rows[qubit][pos] = f"-- {inst.abbreviation(qubit)} --"

        # every line consists of ket-pre- and -suffix with the entries (empty or instruction) separated by +
        lines = [f"| q{q} {Instruction.__circuit_input_value(q, state_vectors)}>" + "+".join(rows[q])
                 + f"< q'{q} {Instruction.__circuit_output_value(q, state_vectors)}" for q in range(num_of_qubits)]
        lines.reverse()  # place qubits from top to bottom, high to low index

        # for some reason the whitespace in front is needed to center the text correctly
        lines[0] = "In " + lines[0] + " Out"
        line_width = len(lines[0])
        return "\n".join([center_string(line, line_width, uneven_left=False) for line in lines])

    def __init__(self, gate_type: GateType, instruction: QiskitGate, needed_qubits: int):
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

    def setup(self, qargs: List[int], cargs: Optional[List[int]] = None, position: Optional[int] = None) \
            -> "Instruction":
        """
        Function used to programmatically set up a gate in one go after instantiation.
        """
        if len(qargs) > self.__needed_qubits:
            Logger.instance().warn(f"Instruction.setup(): {len(qargs)} qubits provided but only {self.__needed_qubits} "
                                   f"needed. Ignoring the over-specified ones.", from_pycui=False)
        if len(qargs) < self.__needed_qubits:
            Logger.instance().warn(f"Instruction.setup(): {len(qargs)} qubits provided but {self.__needed_qubits} "
                                   f"needed. Things might not work correctly due to under-specified qubits.",
                                   from_pycui=False)
        for qubit in qargs:
            self.use_qubit(qubit)
        if cargs is not None:
            self._cargs = cargs
        if position is not None:
            self.use(position)
        return self

    def reset(self, skip_qargs: bool = False, skip_position: bool = False):
        if not skip_qargs:
            self._qargs = []
        if not skip_position:
            self.__position = None

    def append_to(self, circuit: QuantumCircuit, inverse: bool = False):
        instruction = self.__instruction.inverse() if inverse else self.__instruction
        circuit.append(instruction, self._qargs, self._cargs)

    def qargs_iter(self) -> Iterator[int]:
        return iter(self._qargs)

    def get_qubit_at(self, index: int = 0) -> int:
        if 0 <= index < len(self._qargs):
            return self._qargs[index]

    def name(self) -> str:
        return f"{self.__type.short_name} Gate"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        if check_unlocks is not None and check_unlocks(Unlocks.ShowEquation.ach_name):
            return self.__type.description + "\n\nMatrix:\n" + self._matrix_string()
        else:
            return self.__type.description

    @abstractmethod
    def abbreviation(self, qubit: int = 0):
        pass

    def _matrix_string(self) -> str:
        # use the real underlying matrix because some Instructions might have parameters
        return CircuitMatrix.matrix_to_string(self.__instruction.to_matrix(), self.num_of_qubits)

    @abstractmethod
    def copy(self) -> "Instruction":
        pass

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
        self._qargs.pop()  # undo setting the next qubit because we only wanted to pretend that we did
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
    def __init__(self, gate_type: GateType, instruction: QiskitGate):
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

    def __init__(self, gate_type: GateType, instruction: QiskitGate, angle: float):
        """
        :param angle: value between 0 and PI (other values possible, but they correspond to an angle in said range)
        """
        super().__init__(gate_type, instruction)
        self.__angle = angle

    @property
    def angle(self) -> float:
        return self.__angle

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        desc = super().description(check_unlocks)  # remove the stated default angle at the end
        # find indices of "°" and the whitespace before that, so we can replace the angle value.
        degree_index = desc.find("°")
        if degree_index <= 0:
            Logger.instance().error(f"No \"°\" in the description of {self.type}!", show=False, from_pycui=False)
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
    def __init__(self, gate_type: GateType, instruction: QiskitGate):
        super(DoubleQubitGate, self).__init__(gate_type, instruction, needed_qubits=2)


class SwapGate(DoubleQubitGate):
    def __init__(self):
        super().__init__(GateType.SwapGate, gates.SwapGate())

    def _internal_abbreviation(self, index: int) -> str:
        if index == 0:
            return "SW0"
        elif index == 1:
            return "SW1"

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


####### Combined Gates #######

class CombinedGate(Instruction):
    def __init__(self, instructions: List[Instruction], needed_qubits: int, label: Optional[str] = None):
        if label is None: label = "BlackBox"
        circuit = QuantumCircuit.from_register(needed_qubits)
        for inst in instructions: inst.append_to(circuit)
        gate = circuit.to_gate(label=label)

        super().__init__(GateType.Combined, gate, needed_qubits)
        self.__gate = gate
        self.__instructions = instructions

        inst_dict: Dict[int, Instruction] = {}
        for i, inst in enumerate(instructions): inst_dict[i] = inst
        self.__circ_repr = Instruction.circuit_to_string(needed_qubits, len(instructions), inst_dict)

        amplitudes = UnitarySimulator().execute(circuit, decimals=QuantumSimulationConfig.DECIMALS)
        self.__matrix = CircuitMatrix(amplitudes, len(instructions))

    def abbreviation(self, qubit: int = 0):
        return " ? "

    def _matrix_string(self) -> str:
        return self.__matrix.to_string()

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        desc = super().description(check_unlocks)
        desc += "\nUnderlying Circuit:\n"
        desc += self.__circ_repr
        return desc

    def copy(self) -> "Instruction":
        # copy the instructions to not accidentally alter the positioning of the underlying Instructions
        instructions = [inst.copy() for inst in self.__instructions]
        return CombinedGate(instructions, self.__gate.num_qubits, self.__gate.label)


####### Gates for internal use only #######

class DebugGate(SingleQubitGate):
    def __init__(self):
        super().__init__(GateType.Debug, gates.RZGate(phi=2.5))

    def abbreviation(self, qubit: int = 0):
        return "deb"

    def copy(self) -> "Instruction":
        return DebugGate()


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

        GateType.Debug: DebugGate(),
    }

    @staticmethod
    def validate() -> bool:
        for val in GateType:
            if val is GateType.Combined: continue  # todo: properly implement for Combined? Or do we have to skip them?
            assert val in InstructionManager.__GATES, f"{val} not defined in InstructionManager.__GATES!"
        return True

    @staticmethod
    def from_type(gate_type: GateType) -> Instruction:
        return InstructionManager.__GATES[gate_type].copy()

    @staticmethod
    def type_from_name(name: str, ignore_gate_suffix: bool = True) -> Optional[GateType]:
        if ignore_gate_suffix and name.lower().endswith("gate"):
            name = name[:-len("gate")]
        for gate_type in GateType:
            if gate_type.is_in_names(name):
                return gate_type
        return None

    @staticmethod
    def instruction_from_name(name: str, ignore_gate_suffix: bool = True) -> Optional[Instruction]:
        gate_type = InstructionManager.type_from_name(name, ignore_gate_suffix)
        if gate_type is None:
            return None
        return InstructionManager.from_type(gate_type)
