import math
from abc import ABC, abstractmethod
from typing import List, Any, Callable, Tuple, Optional, Dict, Union

from py_cui import ColorRule
from py_cui.widget_set import WidgetSet
from py_cui.widgets import BlockLabel

from qrogue.game.logic.actors import Robot
from qrogue.game.logic.base import StateVector, CircuitMatrix
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.util import Controls, Keys, Logger, Options, ColorCode, Config, ColorConfig, HudConfig, GameplayConfig, \
    QuantumSimulationConfig, InstructionConfig
from qrogue.util.util_functions import center_string, align_string, to_binary_string, int_to_fixed_len_str

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

    def reset_text_color_rules(self) -> None:
        self._text_color_rules.clear()

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

    def reset_text_color_rules(self) -> None:
        for w in self.__widgets:
            w.reset_text_color_rules()

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

    def set_data(self, data: str) -> None:
        self.__text = str(data)

    def render(self) -> None:
        self.widget.set_title(self.__text)

    def render_reset(self, reset_text: bool = True) -> None:
        if reset_text: self.__text = ""
        self.widget.set_title("")

    def __str__(self):
        return f"SimpleWidget(\"{self.__text}\")"


class HudWidget(Widget):
    __MAP_NAME = ""
    __SCORE_LENGTH = 5

    def __init__(self, widget: MyMultiWidget):
        super().__init__(widget)
        self.__robot = None
        self.__map_name = None
        self.__details = None
        self.__render_duration = None

    def set_data(self, data: Tuple[Robot, Optional[str], Optional[str]]) -> None:
        """
        :param data: Tuple of up to three data-items
                - data[0]: Robot
                - data[1]: name of the current map
                - data[2]: text for the situational HUD
        """
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
            if HudConfig.ShowScore:
                text += f"Score: {int_to_fixed_len_str(self.__robot.score, length=HudWidget.__SCORE_LENGTH)}  "
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
    class PlaceHolderData:
        def __init__(self, gate: Optional[Instruction], pos: int = -1, qubit: int = 0):
            self.gate = gate
            self.pos = pos
            self.qubit = qubit

        def resolve(self) -> Tuple[int, int]:
            return self.pos, self.qubit

        def can_change_position(self) -> bool:
            return self.gate is None or self.gate.no_qubits_specified

        def is_valid_qubit(self, qubit: int) -> bool:
            return self.gate is None or self.gate.can_use_qubit(qubit)

        def is_valid_pos(self, pos: int, robot: Robot) -> bool:
            # if gate is None we search for an occupied position (gate_used_at(pos) is not None)
            # if gate is not None we search for a free position (gate_used_at(pos) is None)
            # hence this xor condition
            return (self.gate is None) != (robot.gate_used_at(pos) is None)

        def place(self) -> bool:
            """

            :return: True if more qubits need to be placed, False otherwise
            """
            if self.gate is not None and self.gate.use_qubit(self.qubit):
                if self.qubit > 0:
                    self.qubit -= 1
                else:
                    self.qubit += 1
                return True
            return False

    def __init__(self, widget: WidgetWrapper, controls: Controls):
        super().__init__(widget)
        self.__robot: Optional[Robot] = None
        self.__input: Optional[StateVector] = None
        self.__target: Optional[StateVector] = None
        self.__place_holder_data: Optional[CircuitWidget.PlaceHolderData] = None

        widget.add_key_command(controls.get_keys(Keys.SelectionUp), self.__move_up)
        widget.add_key_command(controls.get_keys(Keys.SelectionRight), self.__move_right)
        widget.add_key_command(controls.get_keys(Keys.SelectionDown), self.__move_down)
        widget.add_key_command(controls.get_keys(Keys.SelectionLeft), self.__move_left)

        widget.activate_individual_coloring()
        ColorRules.apply_circuit_rules(widget)

    def __circuit_input_value(self, qubit: int) -> str:
        if self.__input is not None and self.__input.is_classical \
                and self.__target is not None and self.__target.is_classical \
                and self.__robot.state_vector.is_classical:     # robot.state_vector cannot be None
            index = self.__input.to_value().index(1)    # find where the amplitude is 1
            # get the respective qubit values but in lsb, so we can use $qubit directly as index
            values = to_binary_string(index, self.__input.num_of_qubits, msb=False)
            return f"= {values[qubit]} "
        else:
            return ""

    def __circuit_output_value(self, qubit: int) -> str:
        if self.__input is not None and self.__input.is_classical \
                and self.__target is not None and self.__target.is_classical \
                and self.__robot.state_vector.is_classical:     # robot.state_vector cannot be None
            index = self.__robot.state_vector.to_value().index(1)    # find where the amplitude is 1
            # get the respective qubit values but in lsb, so we can use $qubit directly as index
            out_values = to_binary_string(index, self.__robot.state_vector.num_of_qubits, msb=False)
            index = self.__target.to_value().index(1)
            target_values = to_binary_string(index, self.__target.num_of_qubits, msb=False)
            is_correct = out_values[qubit] == target_values[qubit]
            equality = ColorConfig.colorize(ColorCode.PUZZLE_CORRECT_AMPLITUDE if is_correct
                                            else ColorCode.PUZZLE_WRONG_AMPLITUDE,
                                            '=' + ('=' if is_correct else '/') + '=')
            return f"= {out_values[qubit]}| {equality} <{target_values[qubit]}|"
        else:
            return "|"

    def __change_position(self, right: bool) -> bool:
        def go_right(position: int) -> Optional[int]:
            if position + 1 >= self.__robot.circuit_space:
                return None
            return position + 1

        def go_left(position: int) -> Optional[int]:
            if position - 1 < 0:
                return None
            return position - 1

        if right:
            pos = go_right(self.__place_holder_data.pos)
        else:
            pos = go_left(self.__place_holder_data.pos)
        if pos is None:
            return False

        # only if we are currently removing a gate or if implicit removal is not allowed we have to check for for other
        # gates
        if self.__place_holder_data.gate is None or \
                not GameplayConfig.get_option_value(Options.allow_implicit_removal, convert=True):
            # go on until we find a valid position for the gate
            while not self.__place_holder_data.is_valid_pos(pos, self.__robot):
                if right:
                    pos = go_right(pos)
                else:
                    pos = go_left(pos)
                if pos is None:
                    return False

        self.__place_holder_data.pos = pos
        self.render()
        return True

    def __move_up(self):
        if self.__place_holder_data:
            qubit = self.__place_holder_data.qubit + 1
            while qubit < self.__robot.num_of_qubits:
                if self.__place_holder_data.is_valid_qubit(qubit):
                    self.__place_holder_data.qubit = qubit
                    self.render()
                    return
                qubit += 1

    def __move_right(self):
        if self.__place_holder_data:
            if self.__place_holder_data.can_change_position():
                self.__change_position(True)

    def __move_down(self):
        if self.__place_holder_data:
            qubit = self.__place_holder_data.qubit - 1
            while qubit >= 0:
                if self.__place_holder_data.is_valid_qubit(qubit):
                    self.__place_holder_data.qubit = qubit
                    self.render()
                    return
                qubit -= 1

    def __move_left(self):
        if self.__place_holder_data:
            if self.__place_holder_data.can_change_position():
                self.__change_position(False)

    def abort_placement(self):
        if self.__place_holder_data is not None:
            if self.__place_holder_data.gate is not None:
                self.__place_holder_data.gate.reset()
            self.__place_holder_data = None
            self.render()
            # todo

    def start_gate_placement(self, gate: Optional[Instruction], pos: int = -1, qubit: int = 0):
        self.__place_holder_data = self.PlaceHolderData(gate, pos, qubit)
        if pos < 0 or self.__robot.circuit_space <= pos:
            # if we're currently not removing a gate and implicit removal is allowed we can definitely start at any
            # position
            if self.__place_holder_data.gate is not None and \
                    GameplayConfig.get_option_value(Options.allow_implicit_removal, convert=True):
                self.__place_holder_data.pos = 0
            else:
                for i in range(self.__robot.circuit_space):
                    if self.__place_holder_data.is_valid_pos(i, self.__robot):
                        self.__place_holder_data.pos = i
                        break

    def place_gate(self) -> Tuple[bool, Optional[Instruction]]:
        """

        :return: True if gate is fully placed, False otherwise (e.g. more qubits need to be placed)
        """
        if self.__place_holder_data:
            if self.__place_holder_data.gate is None:
                # remove the instruction
                gate = self.__robot.gate_used_at(self.__place_holder_data.pos)
                if gate is not None:
                    self.__robot.remove_instruction(gate)
                    self.__place_holder_data = None
                    self.render()
                    return True, None
            else:
                if self.__place_holder_data.place():
                    self.render()
                    return False, self.__place_holder_data.gate
                if self.__robot.use_instruction(self.__place_holder_data.gate, self.__place_holder_data.pos):
                    gate = self.__place_holder_data.gate
                    self.__place_holder_data = None
                    return True, gate
                Logger.instance().error("Place_Gate() did not work correctly", show=False, from_pycui=False)
        return False, None

    def set_data(self, data: Tuple[Robot, Optional[Tuple[StateVector, StateVector]]]) -> None:
        self.__robot, vectors = data
        if vectors is None:
            self.__input, self.__target = None, None
        else:
            self.__input, self.__target = vectors

    def render(self) -> None:
        if self.__robot is not None:
            entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
            rows = [[entry] * self.__robot.circuit_space for _ in range(self.__robot.num_of_qubits)]
            for i in range(self.__robot.circuit_space):
                inst = self.__robot.gate_used_at(i)
                if inst:
                    for q in inst.qargs_iter():
                        inst_str = center_string(inst.abbreviation(q), InstructionConfig.MAX_ABBREVIATION_LEN)
                        rows[q][i] = f"--{{{inst_str}}}--"

            if self.__place_holder_data:
                gate = self.__place_holder_data.gate
                pos = self.__place_holder_data.pos
                qubit = self.__place_holder_data.qubit
                if gate is None:
                    rows[qubit][pos] = "--/   /--"
                else:
                    for q in gate.qargs_iter():
                        rows[q][pos] = f"--{{{gate.abbreviation(q)}}}--"
                    rows[qubit][pos] = f"-- {gate.abbreviation(qubit)} --"

            circ_str = " In "   # for some reason the whitespace in front is needed to center the text correctly
            # place qubits from top to bottom, high to low index
            for q in range(len(rows) - 1, -1, -1):
                circ_str += f"| q{q} {self.__circuit_input_value(q)}>"
                row = rows[q]
                for i in range(len(row)):
                    circ_str += row[i]
                    if i < len(row) - 1:
                        circ_str += "+"
                circ_str += f"< q'{q} {self.__circuit_output_value(q)}"
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
        self.__map: Optional[Map] = None
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
            x = self.__map.robot_pos.x
            y = self.__map.robot_pos.y
            rows[y] = rows[y][0:x] + self.__map.robot_img + rows[y][x + 1:]

            self.widget.set_title("\n".join(rows))

    def render_reset(self) -> None:
        self.__backup = self.widget.get_title().title()
        self.widget.set_title("")

    def move(self, direction: Direction) -> bool:
        return self.__map.move(direction)

    def undo_last_move(self) -> bool:
        if self.__map is not None:
            return self.__map.undo_last_move()
        return False


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

    @property
    def can_display_all_content(self) -> bool:
        width, height = self.widget.get_abs_size()
        content = self._stv_str_rep
        if len(content) > 0:
            lines = content.splitlines(keepends=False)
            max_line_len = max([len(line) for line in lines])
            return max_line_len <= width and len(lines) <= height
        else:
            return True

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
        self._stv_str_rep = self._headline + state_vector.to_string()


class OutputStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget, headline)
        widget.activate_individual_coloring()

    def set_data(self, state_vectors: Tuple[StateVector, StateVector], target_reached: bool = False) -> None:
        """

        Args:
            state_vectors: Tuple of the output statevector to display and its diff to a target statevector to color the
                            output correspondingly
            target_reached: _no longer in use_

        Returns: None

        """
        output_stv, diff_stv = state_vectors

        def wrap(skip_ket: bool):
            return [
                output_stv.wrap_in_qubit_conf(
                    i, coloring=True,
                    # check if diff is small enough
                    correct_amplitude=abs(diff_stv.at(i)) <= QuantumSimulationConfig.TOLERANCE,
                    skip_ket=skip_ket)
                for i in range(output_stv.size)     # do it for every qubit combination
            ]

        lines = wrap(skip_ket=False)
        # check if the content fits its widget
        max_line_len = max([len(line) for line in lines])
        width, _ = self.widget.get_abs_size()
        if max_line_len > width: lines = wrap(skip_ket=True)    # shrink content by removing ket

        self._stv_str_rep = self._headline + "\n".join(lines)


class TargetStateVectorWidget(StateVectorWidget):
    def __init__(self, widget: WidgetWrapper, headline: str):
        super().__init__(widget, headline)

    def set_data(self, state_vector: StateVector) -> None:
        def wrap(skip_ket: bool):   # wrap values according to TargetStv specifics (show percentages)
            return [
                state_vector.wrap_in_qubit_conf(
                    i, coloring=False, show_percentage=True,
                    skip_ket=skip_ket)
                for i in range(state_vector.size)  # do it for every qubit combination
            ]

        lines = wrap(skip_ket=False)
        # check if the content fits its widget
        max_line_len = max([len(line) for line in lines])
        width, _ = self.widget.get_abs_size()

        # "-2" is magic number found by trial and error that gives feasible results (perfect visual results are hard
        # since it also depends on font and other spacings); possible explanation: coloring of ket needs 2 chars on the
        # right end, meaning if they would be the only cut-off PyCUI could be smart enough to still color it
        if max_line_len > width-2:
            lines = wrap(skip_ket=True)  # shrink content by removing ket
            # add whitespace so headline is not in the center but more above the amplitudes for better visuals
            split_index = self._headline.index("\n")
            headline = self._headline[:split_index] + " " * QuantumSimulationConfig.MAX_PERCENTAGE_SPACE \
                + self._headline[split_index:]
            self._stv_str_rep = headline + "\n".join(lines)
        else:
            self._stv_str_rep = self._headline + "\n".join(lines)


class CircuitMatrixWidget(Widget):
    def __init__(self, widget: WidgetWrapper):
        super().__init__(widget)
        self.__matrix_str_rep = None
        ColorRules.apply_heading_rules(widget)
        ColorRules.apply_qubit_config_rules(widget)

    @property
    def can_display_all_content(self) -> bool:
        width, height = self.widget.get_abs_size()
        content = self.__matrix_str_rep
        if len(content) > 0:
            lines = content.splitlines(keepends=False)
            max_line_len = max([len(line) for line in lines])
            return max_line_len <= width and len(lines) <= height
        return True

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
        self.__callbacks: List[Union[Callable[[], Optional[bool]]], Callable[[int], Optional[bool]]] = []
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

    def set_data(self, data: Union[
        Tuple[
            Union[List[str], Tuple[List[str], List[Any]]],
            Union[List[Callable[[], Optional[bool]]], Callable[[int], Optional[bool]]]
        ],
        List[Tuple[Union[str, Tuple[str, Any]], Callable[[], Optional[bool]]]]
    ]) -> None:
        """
        Arguments:
            data: selection text and corresponding action callback either as

                1) List of str (=texts), List of callback() or callback(index)  (=actions),

                2) List of (str, Any) (=tuples of text and object connected to the text),
                    List of callback() or callback(index)  (=actions)

                3) List of (str, callback) (=tuples of text and corresponding action)

                4) List of ((str, Any), callback) (=tuples of (text, object) and corresponding action
        """
        assert len(data) >= 1, "set_data() called with empty data!"

        self.render_reset()

        if isinstance(data, list):
            self.__choices = []
            self.__callbacks = []
            for elem in data:
                self.__choices.append(elem[0])
                self.__callbacks.append(elem[1])
        else:
            self.__choices, callbacks = data
            if isinstance(callbacks, list): self.__callbacks = callbacks
            else: self.__callbacks = [callbacks]

        if isinstance(self.__choices, tuple):
            self.__choices, self.__choice_objects = self.__choices

        if self.__columns > 1:
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
            aligned_rows = [align_string(row, max_row_len) for row in rows]
            self.widget.set_title("\n".join(aligned_rows))

    def render_reset(self) -> None:
        self.widget.set_title("")
        self.__index = 0
        # This content reset is needed because changes to other widgets can cause this to render, making the reset
        # pointless if content is still set. Should this lead to any problems somewhere, a new flag-parameter can be
        # added.
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
    def __init__(self, widgets: List[Widget], render_widgets: bool, save_initial_state: bool = True):
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

    def _back(self, render: bool):
        self.__index -= 1
        self.__index = max(self.__index, 0)
        if render: self.render()

    def _forth(self, render: bool):
        self.__index += 1
        self.__index = min(self.__index, len(self.__history) - 1)
        if render: self.render()

    def travel(self, forth: bool, render: bool = True):
        if forth:   self._forth(render)
        else:       self._back(render)

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



