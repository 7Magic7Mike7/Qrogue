import math
from abc import ABC, abstractmethod
from typing import List, Any, Callable, Tuple, Optional

from py_cui import ColorRule
from py_cui.widgets import BlockLabel

from qrogue.game.logic import StateVector
from qrogue.game.logic.actors import Robot, CircuitMatrix
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.util import ColorConfig, Controls, Keys, Logger, Config, HudConfig

from qrogue.graphics.widgets import Renderable
from qrogue.util.config import ColorCode, QuantumSimulationConfig, InstructionConfig
from qrogue.util.util_functions import center_string, align_string


class MyBaseWidget(BlockLabel):
    def __init__(self, wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger):
        super().__init__(wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger)

    def reposition(self, row: int = None, column: int = None, row_span: int = None, column_span: int = None):
        if row:
            self._row = row
        if column:
            self._column = column
        if row_span:
            self._row_span = row_span
        if column_span:
            self._column_span = column_span

    def set_title(self, title: str) -> None:
        super(MyBaseWidget, self).set_title(title)

    def get_title(self) -> str:
        return super(MyBaseWidget, self).get_title()

    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = [0, 1], include_whitespace: bool = False, selected_color = None)\
            -> None:
        super(MyBaseWidget, self).add_text_color_rule(regex, color, rule_type, match_type, region, include_whitespace,
                                                      selected_color)

    def activate_individual_coloring(self):
        regex = ColorConfig.REGEX_TEXT_HIGHLIGHT
        self._text_color_rules.append(
            ColorRule(f"{regex}.*?{regex}", 0, 0, "contains", "regex", [0, 1], False, Logger.instance())
        )

    def add_key_command(self, keys: List[int], command: Callable[[], Any]) -> Any:
        for key in keys:
            super(MyBaseWidget, self).add_key_command(key, command)


class Widget(Renderable, ABC):
    __MOVE_FOCUS = None

    @staticmethod
    def set_move_focus_callback(move_focus: Callable[[MyBaseWidget, Any], None]):
        Widget.__MOVE_FOCUS = move_focus

    @staticmethod
    def move_focus(widget: "Widget", widget_set: Any):
        if Widget.__MOVE_FOCUS:
            Widget.__MOVE_FOCUS(widget.widget, widget_set)

    def __init__(self, widget: MyBaseWidget):
        self.__widget = widget

    @property
    def widget(self) -> MyBaseWidget:
        return self.__widget

    @abstractmethod
    def set_data(self, data) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def render_reset(self) -> None:
        pass


class SimpleWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__text = ""

    def set_data(self, data) -> None:
        self.__text = str(data)

    def render(self) -> None:
        self.widget.set_title(self.__text)

    def render_reset(self) -> None:
        self.__text = ""
        self.widget.set_title("")


class HudWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__robot = None
        self.__map_name = None
        self.__render_duration = None

    def set_data(self, data: Tuple[Robot, Optional[str]]) -> None:
        self.__robot = data[0]
        if data[1]:
            self.__map_name = data[1]

    def reset_data(self) -> None:
        self.__robot = None

    def update_render_duration(self, duration: float):
        if Config.debugging():
            self.__render_duration = duration * 1000

    def render(self) -> None:
        text = ""
        if HudConfig.ShowMapName and self.__map_name:
            text += f"{self.__map_name}\t"
        if self.__robot:
            if HudConfig.ShowEnergy:
                text += f"Energy: {self.__robot.cur_energy} / {self.__robot.max_energy}   \t"
            if HudConfig.ShowKeys:
                text += f"{self.__robot.key_count()} keys  \t"
            if HudConfig.ShowCoins:
                text += f"{self.__robot.backpack.coin_count}$  \t"
        if HudConfig.ShowFPS and self.__render_duration:
            text += f"\t\t{self.__render_duration:.2f} ms"
        self.widget.set_title(text)

    def render_reset(self) -> None:
        self.widget.set_title("")


class CircuitWidget(Widget):
    def __init__(self, widget: MyBaseWidget, controls: Controls):
        super().__init__(widget)
        self.__robot = None
        self.__place_holder_data = None
        # highlight everything between {} (gates), |> (start) or <| (end) or | | (In/Out label)
        regex_gates = "\{.*?\}"
        regex_start = "\|.*?\>"
        regex_end = "\<.*?\|"
        widget.add_text_color_rule(f"({regex_gates}|{regex_start}|{regex_end})",
                                   ColorConfig.CIRCUIT_COLOR, 'contains', match_type='regex')
        regex_label = "In|Out"
        widget.add_text_color_rule(f"({regex_label})", ColorConfig.CIRCUIT_LABEL_COLOR, 'contains', match_type='regex')

        widget.add_key_command(controls.get_keys(Keys.SelectionUp), self.__move_up)
        widget.add_key_command(controls.get_keys(Keys.SelectionRight), self.__move_right)
        widget.add_key_command(controls.get_keys(Keys.SelectionDown), self.__move_down)
        widget.add_key_command(controls.get_keys(Keys.SelectionLeft), self.__move_left)
        #widget.add_key_command(controls.get_keys(Keys.Cancel), self.__abort_placement)

    def __move_up(self):
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            qubit += 1
            while qubit < self.__robot.num_of_qubits:
                if gate.can_use_qubit(qubit):
                    self.__place_holder_data = gate, pos, qubit
                    self.render()
                    return
                qubit += 1

    def __move_right(self):
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            if gate.no_qubits_specified:
                pos += 1
                # go right until we find a free space for the circuit
                while pos < self.__robot.circuit_space:
                    if self.__robot.gate_at(pos) is None:
                        self.__place_holder_data = gate, pos, qubit
                        self.render()
                        return
                    pos += 1

    def __move_down(self):
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            qubit -= 1
            while qubit >= 0:
                if gate.can_use_qubit(qubit):
                    self.__place_holder_data = gate, pos, qubit
                    self.render()
                    return
                qubit -= 1

    def __move_left(self):
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            if gate.no_qubits_specified:
                pos -= 1
                while pos >= 0:
                    if self.__robot.gate_at(pos) is None:
                        self.__place_holder_data = gate, pos, qubit
                        self.render()
                        return
                    pos -= 1

    def __abort_placement(self):
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            # todo

    def start_gate_placement(self, gate: Instruction):
        first_free_spot = -1
        for i in range(self.__robot.circuit_space):
            if self.__robot.gate_at(i) is None:
                first_free_spot = i
                break
        if 0 <= first_free_spot < self.__robot.circuit_space:
            self.__place_holder_data = gate, first_free_spot, 0

    def place_gate(self) -> bool:
        if self.__place_holder_data:
            gate, pos, qubit = self.__place_holder_data
            if gate.use_qubit(qubit):
                if qubit > 0:
                    self.__place_holder_data = gate, pos, qubit-1
                else:
                    self.__place_holder_data = gate, pos, qubit+1
                    self.render()
                return False
            if self.__robot.use_instruction(gate, pos):
                self.__place_holder_data = None
                return True
            Logger.instance().error("Place_Gate() did not work correctly")
        return False

    def set_data(self, robot: Robot) -> None:
        self.__robot = robot

    def render(self) -> None:
        if self.__robot is not None:
            entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
            rows = [[entry] * self.__robot.circuit_space for _ in range(self.__robot.num_of_qubits)]
            for i in range(self.__robot.circuit_space):
                inst = self.__robot.gate_at(i)
                if inst:
                    for q in inst.qargs_iter():
                        inst_str = center_string(inst.abbreviation(q), InstructionConfig.MAX_ABBREVIATION_LEN)
                        rows[q][i] = f"--{{{inst_str}}}--"

            if self.__place_holder_data:
                gate, pos, qubit = self.__place_holder_data
                for q in gate.qargs_iter():
                    rows[q][pos] = f"--{{{gate.abbreviation(q)}}}--"
                rows[qubit][pos] = f"-- {gate.abbreviation(qubit)} --"

            circ_str = " In "
            # place qubits from top to bottom, high to low index
            for q in range(len(rows) - 1, -1, -1):
                circ_str += f"| q{q} >---"
                row = rows[q]
                for i in range(len(row)):
                    circ_str += row[i]
                    if i < len(row) - 1:
                        circ_str += "+"
                circ_str += f"< q'{q} |"
                if q == len(rows) - 1:
                    circ_str += " Out "
                circ_str += "\n"

            self.widget.set_title(circ_str)

    def render_reset(self) -> None:
        self.widget.set_title("")


class MapWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__map = None
        self.__backup = None

    def set_data(self, map_: Map) -> None:
        self.__map = map_

    def render(self) -> None:
        if self.__map is not None:
            rows = self.__map.row_strings()
            # add robot
            x = self.__map.controllable_pos.x
            y = self.__map.controllable_pos.y
            rows[y] = rows[y][0:x] + self.__map.controllable_tile.get_img() + rows[y][x + 1:]

            self.widget.set_title("\n".join(rows))

    def render_reset(self) -> None:
        self.__backup = self.widget.get_title().title()
        self.widget.set_title("")

    def move(self, direction: Direction) -> bool:
        return self.__map.move(direction)


class StateVectorWidget(Widget):
    def __init__(self, widget: MyBaseWidget, headline: str):
        super().__init__(widget)
        self.__headline = headline
        self._stv_str_rep = None
        widget.add_text_color_rule("~.*~", ColorConfig.STV_HEADING_COLOR, 'contains', match_type='regex')

    @property
    def _headline(self) -> str:
        return self.__headline

    def set_data(self, state_vector: StateVector) -> None:
        self._stv_str_rep = f"~{self.__headline}~\n{state_vector.to_string()}"

    def render(self) -> None:
        if self._stv_str_rep:
            self.widget.set_title(self._stv_str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")


class OutputStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: MyBaseWidget, headline: str):
        super().__init__(widget, headline)
        widget.activate_individual_coloring()

    def set_data(self, state_vectors: Tuple[StateVector, StateVector], target_reached: bool = False) -> None:
        output_stv, diff_stv = state_vectors
        stv_rows = output_stv.to_string().split('\n')
        for i in range(diff_stv.size):
            if abs(diff_stv.at(i)) <= QuantumSimulationConfig.TOLERANCE: # or target_reached:
                stv_rows[i] = ColorConfig.colorize(ColorCode.CORRECT_AMPLITUDE, stv_rows[i])
            else:
                stv_rows[i] = ColorConfig.colorize(ColorCode.WRONG_AMPLITUDE, stv_rows[i])
        self._stv_str_rep = f"~{self._headline}~\n" + "\n".join(stv_rows)


class TargetStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: MyBaseWidget, headline: str):
        super().__init__(widget, headline)

    def set_data(self, state_vector: StateVector) -> None:
        self._stv_str_rep = f"~{self._headline}~\n"
        rows = [""] * state_vector.size
        for i in range(state_vector.size):
            rows[i] = center_string(StateVector.complex_to_string(state_vector.at(i)),
                                    QuantumSimulationConfig.MAX_SPACE_PER_NUMBER)
            rows[i] += f"  ({StateVector.complex_to_amplitude_percentage_string(state_vector.at(i))})"

        max_row_len = max([len(row) for row in rows])
        rows = [align_string(row, max_row_len) for row in rows]
        self._stv_str_rep += "\n".join(rows)


class CircuitMatrixWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__matrix_str_rep = None
        widget.add_text_color_rule("~.*~", ColorConfig.STV_HEADING_COLOR, 'contains', match_type='regex')

    def set_data(self, matrix: CircuitMatrix) -> None:
        self.__matrix_str_rep = f"~Circuit Matrix~\n"
        if matrix.num_of_qubits > 3:
            self.__matrix_str_rep += "\n" * int(0.5 * matrix.size - 1)
            self.__matrix_str_rep += "Matrix is too big to be displayed!\n"
            # self.__matrix_str_rep += "But you can have a look at it by opening:\n"
            # self.__matrix_str_rep += " \"TODO\""        # todo create html file of current matrix?
        else:
            self.__matrix_str_rep += matrix.to_string()

    def render(self) -> None:
        if self.__matrix_str_rep is not None:
            self.widget.set_title(self.__matrix_str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")


class QubitInfoWidget(Widget):
    def __init__(self, widget: MyBaseWidget, left_aligned: bool = True):
        super(QubitInfoWidget, self).__init__(widget)
        self.__left_aligned = left_aligned
        self.__text = ""
        widget.add_text_color_rule("~.*~", ColorConfig.QUBIT_INFO_COLOR, 'contains', match_type='regex')

    def set_data(self, num_of_qubits: int) -> None:
        head = ""
        body = ""
        box_left = "|" + " " * 2
        box_right = " " * 2 + "|"
        if self.__left_aligned:
            head_range = range(num_of_qubits-1, -1, -1)
        else:
            head_range = range(num_of_qubits)

        for i in head_range:
            head += f" q{i} "
        # skip 1 character left because of the additional ~ and 2 right because of the qubit index and ~
        head = box_left[:-1] + "~" + head[1:-1] + "~" + box_right[2:]

        for i in range(2 ** num_of_qubits):
            bin_num = bin(i)[2:]    # get rid of the '0b' at the beginning of the binary representation
            bin_num = bin_num.rjust(num_of_qubits, '0')     # add 0s to the beginning (left) by justifying the text to
                                                            # the right
            row = "   ".join(bin_num)  # separate the digits in the string with spaces
            if not self.__left_aligned:
                row = row[::-1]     # [::-1] reverses the list so q0 is on the left
            body += box_left + row + box_right
            body += "\n"

        self.__text = head + "\n" + body
        self.widget.set_title(self.__text)

    def render(self) -> None:
        # self.widget.set_title(self.__text)
        pass

    def render_reset(self) -> None:
        self.widget.set_title("")


class SelectionWidget(Widget):
    __SELECTION_MARKER = "-> "
    __SEPARATOR = " " * len(__SELECTION_MARKER)

    @staticmethod
    def wrap_in_hotkey_str(options: List[str]) -> List[str]:
        if len(options) <= 1:
            return options      # no explicit hotkeys if there are not multiple options
        wrapped_options = []
        for i, option in enumerate(options):
            wrapped_options.append(f"[{i}] {option}")
        return wrapped_options

    def __init__(self, widget: MyBaseWidget, controls: Controls, columns: int = 1, is_second: bool = False,
                 stay_selected: bool = False):
        super(SelectionWidget, self).__init__(widget)
        self.__columns = columns
        self.__is_second = is_second
        self.__stay_selected = stay_selected
        self.__index = 0
        self.__choices = []
        self.__callbacks = []
        self.widget.add_text_color_rule(f"->", ColorConfig.SELECTION_COLOR, 'contains', match_type='regex')

        # init keys
        self.widget.add_key_command(controls.get_keys(Keys.SelectionUp), self.up)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionUp), self.up)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionRight), self.right)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionDown), self.down)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionLeft), self.left)

        # sadly cannot use a loop here because of how lambda expressions work the index would be the same for all calls
        # instead we use a list of indices to still be flexible without changing much code
        indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        hotkeys = [
            controls.get_keys(Keys.HotKey0),
            controls.get_keys(Keys.HotKey1),
            controls.get_keys(Keys.HotKey2),
            controls.get_keys(Keys.HotKey3),
            controls.get_keys(Keys.HotKey4),
            controls.get_keys(Keys.HotKey5),
            controls.get_keys(Keys.HotKey6),
            controls.get_keys(Keys.HotKey7),
            controls.get_keys(Keys.HotKey8),
            controls.get_keys(Keys.HotKey9),
        ]
        self.widget.add_key_command(hotkeys[indices[0]], lambda: self.__jump_to_index(indices[0]))
        self.widget.add_key_command(hotkeys[indices[1]], lambda: self.__jump_to_index(indices[1]))
        self.widget.add_key_command(hotkeys[indices[2]], lambda: self.__jump_to_index(indices[2]))
        self.widget.add_key_command(hotkeys[indices[3]], lambda: self.__jump_to_index(indices[3]))
        self.widget.add_key_command(hotkeys[indices[4]], lambda: self.__jump_to_index(indices[4]))
        self.widget.add_key_command(hotkeys[indices[5]], lambda: self.__jump_to_index(indices[5]))
        self.widget.add_key_command(hotkeys[indices[6]], lambda: self.__jump_to_index(indices[6]))
        self.widget.add_key_command(hotkeys[indices[7]], lambda: self.__jump_to_index(indices[7]))
        self.widget.add_key_command(hotkeys[indices[8]], lambda: self.__jump_to_index(indices[8]))
        self.widget.add_key_command(hotkeys[indices[9]], lambda: self.__jump_to_index(indices[9]))

    @property
    def columns(self) -> int:
        return self.__columns

    @property
    def rows(self) -> int:
        return math.ceil(self.num_of_choices / self.columns)

    @property
    def num_of_choices(self) -> int:
        return len(self.__choices)

    @property
    def index(self) -> int:
        return self.__index

    def update_text(self, text: str, index: int):
        if 0 <= index < len(self.__choices):
            self.__choices[index] = text

    def clear_text(self):
        self.__choices = []
        self.__callbacks = []

    def set_data(self, data: "tuple of list of str and list of SelectionCallbacks") -> None:
        self.render_reset()
        self.__choices, self.__callbacks = data
        choice_length = 0
        for choice in self.__choices:
            if len(choice) > choice_length:
                choice_length = len(choice)
        for i in range(len(self.__choices)):
            self.__choices[i] = self.__choices[i].ljust(choice_length)

    def render(self) -> None:
        rows = [""] * self.rows
        cur_row = 0
        for i in range(self.num_of_choices):
            if i == self.__index and (self.widget.is_selected() or self.__stay_selected):
                rows[cur_row] += SelectionWidget.__SELECTION_MARKER
            else:
                rows[cur_row] += SelectionWidget.__SEPARATOR
            rows[cur_row] += self.__choices[i]
            rows[cur_row] += " "
            if i % self.__columns == self.__columns - 1:
                cur_row += 1
            else:
                rows[cur_row] += SelectionWidget.__SEPARATOR

        if len(rows) > 0:   # simple validity check since some selections are dynamically created during runtime
            max_row_len = max([len(row) for row in rows])
            aligned_rows = [align_string(row, max_row_len) for row in rows]
            self.widget.set_title("\n".join(aligned_rows))

    def render_reset(self) -> None:
        self.widget.set_title("")
        self.__index = 0
        if self.__is_second:
            self.clear_text()

    def validate_index(self) -> bool:
        if self.__index < 0:
            self.__index = 0
            return False
        if len(self.__choices) <= self.__index:
            self.__index = len(self.__choices) - 1
            return False
        return True

    def __single_next(self) -> None:
        self.__index += 1
        if self.__index >= self.num_of_choices:
            self.__index = 0

    def __single_prev(self) -> None:
        self.__index -= 1
        if self.__index < 0:
            self.__index = self.num_of_choices - 1

    def __up(self) -> None:
        if self.num_of_choices <= 1:
            return
        if self.num_of_choices <= self.__columns or self.__columns == 1:
            self.__single_prev()
        else:
            # special case for first line
            if self.__index < self.__columns:
                left_most = self.num_of_choices - self.num_of_choices % self.__columns
                self.__index = left_most + min(self.__index, self.num_of_choices % self.__columns - 1)
            else:
                self.__index -= self.__columns
        self.render()

    def __right(self) -> None:
        if self.num_of_choices <= 1:
            return
        if self.__columns == 1 or self.num_of_choices <= self.__columns:
            self.__single_next()
        else:
            self.__index += 1
            if self.__index >= self.num_of_choices:
                self.__index -= (self.__index % self.__columns)
            elif self.__index % self.__columns == 0:
                self.__index -= self.__columns
        self.render()

    def __down(self) -> None:
        if self.num_of_choices <= 1:
            return
        if self.num_of_choices <= self.__columns or self.__columns == 1:
            self.__single_next()
        else:
            # special case if we are currently in the last line
            if self.__index >= self.num_of_choices - (self.num_of_choices % self.__columns):
                self.__index = self.__index % self.__columns
            else:
                self.__index += self.__columns
                if self.__index >= self.num_of_choices:
                    self.__index = self.num_of_choices - 1
        self.render()

    def __left(self) -> None:
        if self.num_of_choices <= 1:
            return
        if self.__columns == 1 or self.num_of_choices <= self.__columns:
            self.__single_prev()
        else:
            # special case if we are currently in the last line
            if self.__index >= self.num_of_choices - (self.num_of_choices % self.__columns):
                self.__index = self.num_of_choices - 1
            else:
                self.__index -= 1
                if self.__index < 0:
                    self.__index += self.__columns
        self.render()

    def __jump_to_index(self, index: int):
        if index < 0:
            self.__index = 0
        elif self.num_of_choices <= index:
            self.__index = self.num_of_choices - 1
        else:
            self.__index = index
        self.render()

    def use(self) -> bool:
        """
        :return: True if the focus should move, False if the focus should stay in this SelectionWidget
        """
        # if only one callback is given, it needs the index as parameter
        if len(self.__callbacks) == 1 and self.num_of_choices > 1:
            ret = self.__callbacks[0](self.__index)
        else:
            if self.__index >= len(self.__callbacks):
                Logger.instance().throw(IndexError(f"Invalid index = {self.__index} for {self.__callbacks}. "
                                                   f"Text of choices: {self.__choices}"))
            ret = self.__callbacks[self.__index]()
        if ret is None:     # move focus if nothing is returned
            return True
        else:
            return ret
