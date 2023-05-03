import math

import qiskit.circuit.library.standard_gates

import qrogue.util.util_functions as uf

from abc import ABC, abstractmethod
from typing import List, Any, Callable, Tuple, Optional, Dict, Union

from py_cui import ColorRule
from py_cui.widget_set import WidgetSet
from py_cui.widgets import BlockLabel

from qrogue.game.logic import StateVector
from qrogue.game.logic.actors import Robot, CircuitMatrix
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.util import ColorConfig, Controls, Keys, Logger, Config, HudConfig, GameplayConfig, Options
from qrogue.util.config import QuantumSimulationConfig, InstructionConfig

from qrogue.graphics import WidgetWrapper
from qrogue.graphics.rendering import ColorRules
from qrogue.graphics.widgets import Renderable


class MyBaseWidget(BlockLabel, WidgetWrapper):
    def __init__(self, wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger):
        super().__init__(wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger)

    def get_pos(self) -> Tuple[int, int]:
        return self._column, self._row

    def get_abs_pos(self) -> Tuple[int, int]:
        return self._start_x, self._start_y

    def get_size(self) -> Tuple[int, int]:
        return self._column_span, self._row_span

    def get_abs_size(self) -> Tuple[int, int]:
        return self._stop_x - self._start_x, self._stop_y - self._start_y

    def is_selected(self) -> bool:
        return super(MyBaseWidget, self).is_selected()

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
        # cannot easily use the original function to draw the border because the renderer draws it directly
        if self._draw_border:
            title = "-" * self._width + "\n" + title
        super(MyBaseWidget, self).set_title(title)

    def get_title(self) -> str:
        return super(MyBaseWidget, self).get_title()

    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = None, include_whitespace: bool = False, selected_color=None)\
            -> None:
        if region is None:
            region = [0, 1]
        super(MyBaseWidget, self).add_text_color_rule(regex, color, rule_type, match_type, region, include_whitespace,
                                                      selected_color)

    def activate_individual_coloring(self):
        regex = ColorConfig.REGEX_TEXT_HIGHLIGHT
        self._text_color_rules.append(
            ColorRule(f"{regex}.*?{regex}", 0, 0, "contains", "regex", [0, 1], False, Logger.instance())
        )

    def add_key_command(self, keys: List[int], command: Callable[[], Any], overwrite: bool = True) -> Any:
        for key in keys:
            if overwrite or key not in self._key_commands:
                super(MyBaseWidget, self).add_key_command(key, command)


class MyMultiWidget(WidgetWrapper):
    @staticmethod
    def get_title_separator() -> str:
        return ">$%<"

    def __init__(self, widgets: List[WidgetWrapper]):
        assert len(widgets) > 0, "Emtpy MultiWidget created!"

        self.__widgets = widgets

        # the minimal (left-top most) position is where this widget starts (like casting a rectangle around all widgets)
        x, y = self.__widgets[0].get_pos()
        ax, ay = self.__widgets[0].get_abs_pos()
        for i in range(1, len(self.__widgets)):
            w = self.__widgets[i]
            # if logical position is smaller, than also absolute is
            wx, wy = w.get_pos()
            if wx < x:
                ax = w.get_abs_pos()[0]
                x = wx
            if wy < y:
                ay = w.get_abs_pos()[1]
                y = wy
        self.__pos = x, y
        self.__abs_pos = ax, ay

        widths: Dict[int, int] = {}     # find out width of the longest row
        heights: Dict[int, int] = {}    # and height of biggest column
        abs_widths: Dict[int, int] = {}
        abs_heights: Dict[int, int] = {}
        for w in self.__widgets:
            col, row = w.get_pos()
            width, height = w.get_size()
            if row not in widths or col + width > widths[row]:
                widths[row] = col + width
                abs_widths[row] = w.get_abs_pos()[0] + w.get_abs_size()[0]
            if col not in heights or row + height > heights[col]:
                heights[col] = row + height
                abs_heights[col] = w.get_abs_pos()[1] + w.get_abs_size()[1]
        self.__size = max(widths) - x, max(heights) - y
        self.__abs_size = max(abs_widths) - ax, max(abs_heights) - ay

    def get_pos(self) -> Tuple[int, int]:
        """
        Column of the left most widget, row of the top most widget. There will not necessarily be a real widget at
        exactly this position.
        :return: x, y / column, row
        """
        return self.__pos

    def get_abs_pos(self) -> Tuple[int, int]:
        return self.__abs_pos

    def get_size(self) -> Tuple[int, int]:
        """
        Width of the widest row and height of the highest column. You can imagine it like fitting the smallest possible
        rectangle around all its widgets.
        :return: width, height
        """
        return self.__size

    def get_abs_size(self) -> Tuple[int, int]:
        return self.__abs_size

    def is_selected(self) -> bool:
        """

        :return: True if one of its widgets is selected
        """
        for w in self.__widgets:
            if w.is_selected():
                return True
        return False

    def reposition(self, row: int = None, column: int = None, row_span: int = None, column_span: int = None):
        if column is None:
            col_diff = None
        else:
            col_diff = column - self.__pos[0]
        if row is None:
            row_diff = None
        else:
            row_diff = row - self.__pos[1]

        if column_span is None:
            width_diff = None
        else:
            width_diff = column_span - self.__size[0]
        if row_span is None:
            height_diff = None
        else:
            height_diff = row_span - self.__size[1]

        old_width, old_height = self.__size
        width_changes = 0
        height_changes = 0
        for i, w in enumerate(self.__widgets):
            w_col, w_row = w.get_pos()
            w_width, w_height = w.get_size()

            new_row = None
            if row_diff is not None:
                new_row = w_row + row_diff

            new_col = None
            if col_diff is not None:
                new_col = w_col + col_diff

            new_row_span = None
            if height_diff is not None:
                h_mul = height_diff * w_height / old_height  # try to keep the same widget_height / whole_height ratio
                height_change = round(w_height * h_mul)
                height_changes += height_change

                if i < len(self.__widgets) - 1 and height_changes < height_diff:
                    new_row_span = w_height + height_change
                else:
                    # give the widget the remaining space
                    new_row_span = height_diff - (height_changes - height_change)

            new_column_span = None
            if width_diff is not None:
                w_mul = width_diff * w_width / old_width    # try to keep the same widget_width / whole_width ratio
                width_change = round(w_width * w_mul)
                width_changes += width_change
                if width_changes < width_diff:
                    new_column_span = w_width + width_change

            # todo definitely needs detailed testing
            w.reposition(row=new_row, column=new_col, row_span=new_row_span, column_span=new_column_span)

        # update to the new values
        self.__pos = column, row
        self.__size = column_span, row_span

    def set_title(self, title: str) -> None:
        self.set_titles(title.split(MyMultiWidget.get_title_separator()))

    def set_titles(self, titles: List[str]):
        for i, t in enumerate(titles):
            if i < len(self.__widgets):
                self.__widgets[i].set_title(t)

    def get_title(self) -> str:
        titles = self.get_titles()
        return MyMultiWidget.get_title_separator().join(titles)

    def get_titles(self) -> List[str]:
        titles = []
        for w in self.__widgets:
            titles.append(w.get_title())
        return titles

    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = None, include_whitespace: bool = False, selected_color=None) -> None:
        """
        Applies the color rule to all of its widgets

        :param regex:
        :param color:
        :param rule_type:
        :param match_type:
        :param region:
        :param include_whitespace:
        :param selected_color:
        :return:
        """
        if region is None:
            region = [0, 1]

        for w in self.__widgets:
            w.add_text_color_rule(regex, color, rule_type, match_type, region, include_whitespace, selected_color)

    def activate_individual_coloring(self):
        for w in self.__widgets:
            w.activate_individual_coloring()

    def add_key_command(self, keys: List[int], command: Callable[[], Any], overwrite: bool = True) -> Any:
        for w in self.__widgets:
            w.add_key_command(keys, command, overwrite)

    def toggle_border(self):
        for w in self.__widgets:
            w.toggle_border()


class Widget(Renderable, ABC):
    __MOVE_FOCUS: Optional[Callable[[WidgetWrapper, WidgetSet], None]] = None

    @staticmethod
    def set_move_focus_callback(move_focus: Callable[[WidgetWrapper, WidgetSet], None]):
        Widget.__MOVE_FOCUS = move_focus

    @staticmethod
    def move_focus(widget: "Widget", widget_set: WidgetSet):
        if Widget.__MOVE_FOCUS:
            Widget.__MOVE_FOCUS(widget.widget, widget_set)

    def __init__(self, widget: WidgetWrapper):
        self.__widget = widget

    @property
    def widget(self) -> WidgetWrapper:
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
    def __init__(self, widget: WidgetWrapper, initial_text: str = ""):
        super().__init__(widget)
        self.__text = initial_text

    def set_data(self, data) -> None:
        self.__text = str(data)

    def render(self) -> None:
        self.widget.set_title(self.__text)

    def render_reset(self) -> None:
        self.__text = ""
        self.widget.set_title("")


class HudWidget(Widget):
    __MAP_NAME = ""

    def __init__(self, widget: MyMultiWidget):
        super().__init__(widget)
        self.__robot = None
        self.__map_name = None
        self.__details = None
        self.__render_duration = None

    def set_data(self, data: Tuple[Robot, Optional[str], Optional[str]]) -> None:
        self.__robot = data[0]
        if data[1] is not None:
            HudWidget.__MAP_NAME = data[1]
        if data[2] is not None:
            self.__details = data[2]
        else:
            self.__details = ""

        self.__map_name = HudWidget.__MAP_NAME

    def update_situational(self, data: str):
        self.__details = data

    def reset_data(self) -> None:
        self.__robot = None
        self.__map_name = None
        self.__details = None

    def update_render_duration(self, duration: float):
        if Config.debugging():
            self.__render_duration = duration * 1000

    def render(self) -> None:
        text = ""
        if HudConfig.ShowMapName and self.__map_name:
            text += f"{self.__map_name}\n"
        if self.__robot:
            if HudConfig.ShowEnergy:
                text += f"Energy: {self.__robot.cur_energy} / {self.__robot.max_energy}   \t"
            if HudConfig.ShowKeys:
                text += f"{self.__robot.key_count()} keys  \t"
            if HudConfig.ShowCoins:
                text += f"{self.__robot.backpack.coin_count}$  \t"
        if HudConfig.ShowFPS and self.__render_duration:
            text += f"\t\t{self.__render_duration:.2f} ms"

        if Config.debugging():
            self.widget.set_title(f"{text}{MyMultiWidget.get_title_separator()}{self.__details}"
                                  f"{MyMultiWidget.get_title_separator()}Debug\n{Config.frame_count()}")
        else:
            self.widget.set_title(f"{text}{MyMultiWidget.get_title_separator()}{self.__details}")

    def render_reset(self) -> None:
        self.widget.set_title("")


class CircuitWidget(Widget):
    class _GateWrapper(Instruction):
        def __init__(self, gate: Instruction):
            # treat it as an IGate to not alter the functionality of the circuit
            super().__init__(gate.type, qiskit.circuit.library.standard_gates.IGate(), 1)
            self.__gate = gate
            self.__cur_qubit = 0

        @property
        def is_done(self) -> bool:
            return self.__gate.all_qubits_specified

        def abbreviation(self, qubit: Optional[int] = None):
            if qubit is None:
                qubit = self.__cur_qubit
            return self.__gate.abbreviation(qubit)

        def copy(self) -> Instruction:
            return CircuitWidget._GateWrapper(self.__gate)

        def unpack(self) -> Instruction:
            return self.__gate

        def next_qubit(self) -> bool:
            """
            :return: True if more qubits are needed for the Instruction to work, False if there are enough
            """
            self.__cur_qubit += 1
            return self.__gate.use_qubit(self.qargs_copy()[0])

        def __str__(self):
            return f"Wrapper[{self.__gate}]"

    class _ActionPlaceHolder(ABC):
        def __init__(self, grid: Robot.CircuitGrid, gate: Optional[Instruction], pos: int = -1, qubit: int = 0):
            self.grid = grid
            if gate is None: self.gate = None
            else: self.gate: CircuitWidget._GateWrapper = CircuitWidget._GateWrapper(gate)
            self.pos = pos
            self.qubit = qubit

        @abstractmethod
        def can_reset_qubits(self) -> bool:
            pass

        @abstractmethod
        def can_change_position(self) -> bool:
            pass

        @abstractmethod
        def is_valid_qubit(self, qubit: int) -> bool:
            pass

        @abstractmethod
        def is_valid_pos(self, pos: int, grid: Robot.CircuitGrid) -> bool:
            # if gate is None we search for an occupied position (gate_used_at(pos) is not None)
            # if gate is not None we search for a free position (gate_used_at(pos) is None)
            # hence this xor condition
            pass

        @abstractmethod
        def perform(self, data: Any = None) -> Tuple[bool, Optional[Instruction]]:
            """

            :return: True if action needs to be confirmed again, False if it is finished
            """
            pass

        @abstractmethod
        def abort(self):
            pass

    class _Place(_ActionPlaceHolder):
        FIX_POSITION = "fix_position"

        def __init__(self, grid: Robot.CircuitGrid, gate: Instruction, pos: int = 0, qubit: int = 0):
            super().__init__(grid, gate, pos, qubit)
            self.__fixed_position = False

        def can_reset_qubits(self) -> bool:
            return self.gate.all_qubits_specified

        def can_change_position(self) -> bool:
            return not self.__fixed_position and (self.gate.no_qubits_specified or self.gate.all_qubits_specified)

        def is_valid_qubit(self, qubit: int) -> bool:
            return self.gate.can_use_qubit(qubit)

        def is_valid_pos(self, pos: int, grid: Robot.CircuitGrid) -> bool:
            # todo: consider implicit removal
            # if GameplayConfig.get_option_value(Options.allow_implicit_removal, convert=True):
            # as long as we have space for a new gate every position is valid (at least True for single qubit gates)
            # todo: test statement for multi qubit gates
            return True     #grid.get(self.qubit, pos) is None

        def perform(self, data: Any = None) -> bool:
            """

            :return: True if more qubits need to be placed (we continue the current action), False otherwise
            """
            fix_performance = data is not None and CircuitWidget._Place.FIX_POSITION in data
            if fix_performance and self.gate.next_qubit() or \
                    not fix_performance and self.gate.use_qubit(self.qubit):
                if self.qubit > 0:
                    self.qubit -= 1
                else:
                    self.qubit += 1

            if self.gate.is_done:
                gate = self.gate.unpack()
                self.grid.remove(self.gate)
            else:
                gate = self.gate
            if self.grid.place(gate, self.pos):
                return not self.gate.is_done
            Logger.instance().error("Place_Gate() did not work correctly", from_pycui=False)
            return False

        def abort(self):
            self.__fixed_position = False
            self.grid.remove(self.gate)
            pass    # todo remove from grid?

    class _Remove(_ActionPlaceHolder):
        def __init__(self, grid: Robot.CircuitGrid):
            super().__init__(grid, None, 0, 0)

        def can_reset_qubits(self) -> bool:
            return False    # we don't store a gate we could reset

        def can_change_position(self) -> bool:
            return True

        def is_valid_qubit(self, qubit: int) -> bool:
            return True

        def is_valid_pos(self, pos: int, grid: Robot.CircuitGrid) -> bool:
            return True     #grid.get(pos, self.qubit) is not None

        def perform(self, data: Any = None) -> bool:
            gate = self.grid.get(self.qubit, self.pos)
            if gate is not None:
                self.grid.remove(gate)
                #self.gate = CircuitWidget._GateWrapper(gate)
            return False    # removing never needs a second step

        def abort(self):
            pass    # nothing to do

    class _Move(_Place):
        def __init__(self, grid: Robot.CircuitGrid, gate: Instruction):
            self.__original_place: Tuple[int, List[int]] = gate.position, gate.qargs_copy()
            super().__init__(grid, gate, self.__original_place[0], self.__original_place[1][0])

        def perform(self, data: Any = None) -> bool:
            pass    # todo

        def abort(self):
            self.grid.remove(self.gate)
            [self.gate.use_qubit(qu) for qu in self.__original_place[1]]    # set original qubits
            self.grid.place(self.gate, self.__original_place[0])            # place on original position

    @staticmethod
    def __dress_instruction_string(inst_str: str, use_separator: bool, include_braces: bool):
        if use_separator: sep = "+"
        else: sep = "-"
        if include_braces: return f"{sep}--{{{inst_str}}}--"
        else: return f"{sep}-- {inst_str} --"

    def __init__(self, widget: WidgetWrapper, controls: Controls):
        super().__init__(widget)
        self.__grid: Optional[Robot.CircuitGrid] = None
        self.__action: Optional[CircuitWidget._ActionPlaceHolder] = None
        self.__in_multi_qubit_performance = False

        widget.add_key_command(controls.get_keys(Keys.SelectionUp), self.__move_up)
        widget.add_key_command(controls.get_keys(Keys.SelectionRight), self.__move_right)
        widget.add_key_command(controls.get_keys(Keys.SelectionDown), self.__move_down)
        widget.add_key_command(controls.get_keys(Keys.SelectionLeft), self.__move_left)

    def __change_position(self, right: bool) -> bool:
        """
        :param right: whether we try to move to the right or left
        :return: True if the position changed, otherwise False
        """
        def move(position: int, right_: bool) -> Optional[int]:
            if right_:
                if position + 1 >= len(self.__grid): return None
                else: return position + 1
            else:
                if position - 1 < 0: return None
                else: return position - 1

        while True:
            pos = move(self.__action.pos, right)
            if pos is None:
                return False
            elif self.__action.is_valid_pos(pos, self.__grid):
                break

        self.__action.pos = pos
        return True

    def __change_qubit(self, up: bool) -> bool:
        def move(qu: int, up_: bool) -> Optional[int]:
            if up_:
                if qu + 1 >= self.__grid.num_of_qubits: return None
                else: return qu + 1
            else:
                if qu - 1 < 0: return None
                else: return qu - 1

        while True:
            qubit = move(self.__action.qubit, up)
            if qubit is None:
                return False
            elif self.__action.is_valid_qubit(qubit):
                break

        self.__action.qubit = qubit
        return True

    def __move_up(self):
        if self.__action is not None:
            self.__grid.load()
            if self.__change_qubit(up=True):
                if self.__action.can_reset_qubits():
                #if not self.__in_multi_qubit_performance:
                    self.__action.gate.reset()      # todo maybe skip_position=True?
                self.__action.perform()
                self.render()

    def __move_right(self):
        if self.__action is not None:
            self.__grid.load()
            if self.__action.can_change_position() and self.__change_position(right=True):
                self.__action.perform()
                self.render()

    def __move_down(self):
        if self.__action is not None:
            self.__grid.load()

            if self.__change_qubit(up=False):
                if self.__action.can_reset_qubits():
                #if not self.__in_multi_qubit_performance:
                    self.__action.gate.reset()      # todo maybe skip_position=True?
                self.__action.perform()
                self.render()

    def __move_left(self):
        if self.__action is not None:
            self.__grid.load()
            if self.__action.can_change_position() and self.__change_position(right=False):
                self.__action.perform()
                self.render()

    def __place_gate(self) -> Tuple[bool, Optional[Instruction]]:
        """

        :return: True if gate is fully placed, False otherwise (e.g. more qubits need to be placed)
        """
        if self.__action is None:
            return False, None

        if self.__action.perform():
            self.render()
            return False, self.__action.gate

        else:
            if self.__grid.place(self.__action.gate, self.__action.pos):  # todo might need a "move" implementation?
                # if self.__robot.use_instruction(self.__place_holder_data.gate, self.__place_holder_data.pos):
                gate = self.__action.gate
                self.__action = None
                return True, gate
        Logger.instance().error("Place_Gate() did not work correctly", from_pycui=False)
        return False, None

    def start_gate_placement(self, gate: Instruction, pos: int = 0, qubit: int = 0):
        pos = uf.clamp(pos, 0, self.__grid.circuit_space - 1)
        self.__action = self._Place(self.__grid, gate, pos, qubit)

        self.__grid.load()      # todo might be unnecessary
        self.__action.perform()
        self.render()

    def start_gate_removal(self):
        self.__action = CircuitWidget._Remove(self.__grid)

    def start_gate_moving(self, gate: Instruction, pos: int = 0, qubit: int = 0):
        pos = uf.clamp(pos, 0, self.__grid.circuit_space - 1)
        self.__action = CircuitWidget._Move(self.__grid, gate, pos, qubit)

    def perform_action(self) -> Tuple[bool, Optional[bool]]:
        if self.__action is None:
            return False, None

        self.__in_multi_qubit_performance = self.__action.perform({CircuitWidget._Place.FIX_POSITION: True})
        self.__grid.save()
        self.render()
        if self.__in_multi_qubit_performance:
            return False, None
        else:
            self.__action = None
            return True, None if isinstance(self.__action, CircuitWidget._Remove) else True

    def abort_action(self):
        if self.__action is not None:
            self.__action.abort()
            self.__action = None
            self.render()
            # todo

    def set_data(self, grid: Robot.CircuitGrid) -> None:
        self.__grid = grid
        self.__grid.save()

    def render(self) -> None:
        if self.__grid is not None:
            currently_removing = isinstance(self.__action, CircuitWidget._Remove)
            entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
            row_len = (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3) * self.__grid.circuit_space

            rows = []
            for qu in range(self.__grid.num_of_qubits):
                row = ""
                for position in range(self.__grid.circuit_space):
                    inst = self.__grid.get(qu, position)
                    if inst is None:
                        if currently_removing and qu == self.__action.qubit and position == self.__action.pos:
                            inst_str = self.__dress_instruction_string(' ' * InstructionConfig.MAX_ABBREVIATION_LEN,
                                                                       position > 0, False)
                        else:
                            inst_str = f"-{entry}"
                    else:
                        inst_str = uf.center_string(inst.abbreviation(qu), InstructionConfig.MAX_ABBREVIATION_LEN)
                        inst_str = self.__dress_instruction_string(inst_str, position > 0, self.__action is None or
                                                                   inst is not self.__action.gate)
                    row += inst_str
                row = row[:-1]  # remove the trailing "+"
                rows.append(uf.center_string(row, row_len))

            """
            if self.__action:
                gate = self.__action.gate
                pos = self.__action.pos
                qubit = self.__action.qubit
                if gate is None:
                    rows[qubit][pos] = "--/   /--"
                else:
                    for q in gate.qargs_iter():
                        rows[q][pos] = f"--{{{gate.abbreviation(q)}}}--"
                    rows[qubit][pos] = f"-- {gate.abbreviation(qubit)} --"
            """

            circ_str = " In "   # for some reason the whitespace in front is needed to center the text correctly
            # place qubits from top to bottom, high to low index
            for q in range(len(rows) - 1, -1, -1):
                circ_str += f"| q{q} >"
                circ_str += rows[q]
                circ_str += f"< q'{q} |"
                if q == len(rows) - 1:
                    circ_str += " Out"
                circ_str += "\n"

            self.widget.set_title(circ_str)

    def render_reset(self) -> None:
        self.widget.set_title("")


class MapWidget(Widget):
    def __init__(self, widget: WidgetWrapper):
        super().__init__(widget)
        self.__map_started = False
        self.__map = None
        self.__backup = None

    def set_data(self, map_: Map) -> None:
        self.__map = map_
        self.__map_started = False

    def try_to_start_map(self):
        if not self.__map_started:
            if self.__map is None:
                Logger.instance().throw(RuntimeError("self.__map is None! Most likely this means that the map could "
                                                     "not be loaded."))
            self.__map.start()
            self.__map_started = True

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
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget)
        self.__headline = headline
        self._stv_str_rep = None
        ColorRules.apply_heading_rules(widget)
        ColorRules.apply_qubit_config_rules(widget)

    @property
    def _headline(self) -> str:
        return f"~{self.__headline}~\n\n"

    def set_data(self, state_vector: StateVector) -> None:
        self._stv_str_rep = self._headline + state_vector.to_string()

    def render(self) -> None:
        if self._stv_str_rep:
            self.widget.set_title(self._stv_str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")


class InputStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget, headline)

    def set_data(self, state_vector: StateVector) -> None:
        # here we only need 1 space per value because every value is either 1 or 0
        self._stv_str_rep = self._headline + state_vector.to_string(space_per_value=1)


class OutputStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget, headline)
        widget.activate_individual_coloring()

    def set_data(self, state_vectors: Tuple[StateVector, StateVector], target_reached: bool = False) -> None:
        output_stv, diff_stv = state_vectors
        self._stv_str_rep = self._headline
        for i in range(output_stv.size):
            correct_amplitude = abs(diff_stv.at(i)) <= QuantumSimulationConfig.TOLERANCE
            self._stv_str_rep += output_stv.wrap_in_qubit_conf(i, coloring=True, correct_amplitude=correct_amplitude)
            self._stv_str_rep += "\n"


class TargetStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget, headline)

    def set_data(self, state_vector: StateVector) -> None:
        self._stv_str_rep = self._headline
        for i in range(state_vector.size):
            self._stv_str_rep += state_vector.wrap_in_qubit_conf(i, show_percentage=True)
            self._stv_str_rep += "\n"


class CircuitMatrixWidget(Widget):
    def __init__(self, widget: WidgetWrapper):
        super().__init__(widget)
        self.__matrix_str_rep = None
        ColorRules.apply_heading_rules(widget)
        ColorRules.apply_qubit_config_rules(widget)

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
    def __init__(self, widget: WidgetWrapper, left_aligned: bool = True):
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
            # add 0s to the beginning (left) by justifying the text to the right
            bin_num = bin_num.rjust(num_of_qubits, '0')
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
            wrapped_options.append(SelectionWidget._wrap_in_hotkey_str(option, i))
        return wrapped_options

    @staticmethod
    def _wrap_in_hotkey_str(text: str, index: int) -> str:
        return f"[{index}] {text}"

    @staticmethod
    def _is_wrapped_in_hotkey_str(text: str, index: int) -> bool:
        return text.startswith(f"[{index}] ")

    def __init__(self, widget: WidgetWrapper, controls: Controls, columns: int = 1, is_second: bool = False,
                 stay_selected: bool = False, on_key_press: Optional[Callable[[Keys], None]] = None):
        super(SelectionWidget, self).__init__(widget)
        self.__columns = columns
        self.__is_second = is_second
        self.__stay_selected = stay_selected

        def okp(key: Keys):
            if on_key_press is not None: on_key_press(key)
        self.__on_key_press = okp
        self.__index = 0
        self.__choices: List[str] = []
        self.__choice_objects: List = []
        self.__callbacks: List[Union[Callable[[], bool]], Callable[[int], bool]] = []
        self.widget.add_text_color_rule(f"->", ColorConfig.SELECTION_COLOR, 'contains', match_type='regex')

        # init keys
        self.widget.add_key_command(controls.get_keys(Keys.SelectionUp), self._up)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionRight), self._right)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionDown), self._down)
        self.widget.add_key_command(controls.get_keys(Keys.SelectionLeft), self._left)

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
    def _width_of_last_row(self) -> int:
        return self.num_of_choices - self._index_of_row_start(self.num_of_choices - 1)  # - start of last row

    @property
    def num_of_choices(self) -> int:
        return len(self.__choices)

    @property
    def index(self) -> int:
        return self.__index

    @property
    def selected_object(self) -> Any:
        if self.__choice_objects is not None and self.index < len(self.__choice_objects):
            return self.__choice_objects[self.index]
        return None

    def _index_of_row_start(self, index: int):
        start_of_last_row = self.columns * (self.rows - 1)
        if index >= start_of_last_row:
            return start_of_last_row
        return index - (index % self.columns)

    def update_text(self, text: str, index: int):
        if 0 <= index < len(self.__choices):
            if SelectionWidget._is_wrapped_in_hotkey_str(self.__choices[index], index):
                self.__choices[index] = SelectionWidget._wrap_in_hotkey_str(text, index)
            else:
                self.__choices[index] = text

    def set_data(self, data: "Tuple[Union[List[str], Tuple[List[str], List[Any]]], List[Callable]]") -> None:
        assert len(data) >= 1, "set_data() called with empty data!"

        self.render_reset()
        self.__choices, self.__callbacks = data

        if isinstance(self.__choices, tuple):
            self.__choices, self.__choice_objects = self.__choices

        choice_length = max([len(choice) for choice in self.__choices])
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
            aligned_rows = [uf.align_string(row, max_row_len) for row in rows]
            self.widget.set_title("\n".join(aligned_rows))

    def render_reset(self) -> None:
        self.widget.set_title("")
        self.__index = 0
        if self.__is_second:
            self.__choices = []
            self.__choice_objects = []
            self.__callbacks = []

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

    def _up(self) -> None:
        if self.num_of_choices <= 1:
            return
        # only call if the key press changes something (e.g. more than 1 choice)
        self.__on_key_press(Keys.SelectionUp)
        if self.num_of_choices <= self.__columns or self.__columns == 1:
            self.__single_prev()
        else:
            # special case for first line
            if self.__index < self.__columns:
                # provides either the very last element or (start of last row + column (== index if in first row))
                self.__index = min(self._index_of_row_start(self.num_of_choices - 1) + self.__index,
                                   self.num_of_choices - 1)
            else:
                self.__index -= self.__columns
        self.render()

    def _right(self) -> None:
        if self.num_of_choices <= 1:
            return
        # only call if the key press changes something (e.g. more than 1 choice)
        self.__on_key_press(Keys.SelectionRight)
        if self.__columns == 1 or self.num_of_choices <= self.__columns:
            self.__single_next()
        else:
            # special case if we are currently at the end of the last row
            if self.__index == self.num_of_choices - 1:
                self.__index = self._index_of_row_start(self.__index)
            # another special case if we are at the end of any other row
            elif self.__index % self.__columns == self.__columns - 1:
                self.__index -= (self.__columns - 1)
            else:
                self.__index += 1
        self.render()

    def _down(self) -> None:
        if self.num_of_choices <= 1:
            return
        # only call if the key press changes something (e.g. more than 1 choice)
        self.__on_key_press(Keys.SelectionDown)
        if self.num_of_choices <= self.__columns or self.__columns == 1:
            self.__single_next()
        else:
            # special case if we are currently in the last line
            if self.__index >= self._index_of_row_start(self.num_of_choices - 1):
                self.__index = self.__index % self.__columns
            else:
                self.__index = min(self.__index + self.__columns, self.num_of_choices - 1)
        self.render()

    def _left(self) -> None:
        if self.num_of_choices <= 1:
            return
        # only call if the key press changes something (e.g. more than 1 choice)
        self.__on_key_press(Keys.SelectionLeft)
        if self.__columns == 1 or self.num_of_choices <= self.__columns:
            self.__single_prev()
        else:
            # special case if we are currently at the start of the last row
            if self.__index == self._index_of_row_start(self.num_of_choices - 1):
                self.__index = self.num_of_choices - 1
            # another special case if we are at the start of any other row
            elif self.__index % self.columns == 0:
                self.__index += self.__columns - 1
            else:
                self.__index -= 1
        self.render()

    def __jump_to_index(self, index: int):
        self.__on_key_press(Keys.hotkeys()[index])      # todo implement more efficiently? On the other hand hotkeys are not that important maybe
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
        self.__on_key_press(Keys.Action)
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


class HistoricWrapperWidget:
    def __init__(self, widgets: Tuple[Widget], render_widgets: bool, save_initial_state: bool = True):
        self.__widgets = widgets
        self.__history: List[Tuple[str]] = []
        self.__index = -1

        if render_widgets:
            for widget in widgets:
                widget.render()     # update the visuals before potentially saving them
        if save_initial_state:
            self.save_state(rerender=True, force=True)

    @property
    def index(self) -> int:
        return self.__index

    @property
    def is_in_past(self) -> bool:
        return self.__index < len(self.__history) - 1

    @property
    def _cur_data(self) -> Optional[Tuple[str]]:
        if 0 <= self.__index < len(self.__history):
            return self.__history[self.__index]
        return None

    def save_state(self, rerender: bool = False, force: bool = False):
        if rerender:
            for widget in self.__widgets:
                widget.render()
        data = tuple([widget.widget.get_title() for widget in self.__widgets])

        # if force is False then data is not saved if it is equal to the latest data
        if force or len(self.__history) <= 0 or data != self.__history[-1]:
            self.__history.append(data)
            self.__index = len(self.__history) - 1  # index points to the last element

    def back(self, render: bool = True):
        self.__index -= 1
        self.__index = max(self.__index, 0)
        if render: self.render()

    def forth(self, render: bool = True):
        self.__index += 1
        self.__index = min(self.__index, len(self.__history) - 1)
        if render: self.render()

    def jump_to_present(self, render: bool = True):
        if self.is_in_past:
            self.__index = len(self.__history) - 1
            if render: self.render()

    def clean_history(self) -> None:
        if len(self.__history) > 0:
            self.__history = [self.__history[-1]]  # only keep the latest element
            self.__index = 0

    def render(self) -> None:
        if self._cur_data is not None:
            assert len(self._cur_data) == len(self.__widgets), "Length of data doesn't match widgets': " \
                                                               f"{len(self._cur_data)} != {len(self.__widgets)}"
            for i, widget in enumerate(self.__widgets):
                widget.widget.set_title(self._cur_data[i])
                #widget.render()


class HistoricProperty(Widget, ABC):
    def __init__(self, widget: WidgetWrapper):
        super().__init__(widget)
        self.__history: List[str] = []
        self.__index = -1

    @property
    def index(self) -> int:
        return self.__index

    @property
    def _cur_data(self) -> Optional[str]:
        if 0 <= self.__index < len(self.__history):
            return self.__history[self.__index]
        return None

    def add_data(self, data: str, force: bool = False):
        # if force is False then data is not saved if it is equal to the latest data
        if force or len(self.__history) <= 0 or data != self.__history[-1]:
            self.__history.append(data)
            self.__index = len(self.__history) - 1  # index points to the last element

    def back(self):
        self.__index -= 1
        self.__index = max(self.__index, 0)

    def forth(self):
        self.__index += 1
        self.__index = min(self.__index, len(self.__history) - 1)

    def clean_history(self) -> None:
        self.__history = [self.__history[-1]]  # only keep the latest element
        self.__index = 0

    def render(self) -> None:
        if self._cur_data is not None:
            self.widget.set_title(self._cur_data)



