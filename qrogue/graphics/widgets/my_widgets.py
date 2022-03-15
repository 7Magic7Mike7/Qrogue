from abc import ABC, abstractmethod
from typing import List, Any, Callable, Tuple, Optional

from py_cui.widgets import BlockLabel

from qrogue.game.logic.actors import Robot
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.util import ColorConfig, Controls, InstructionConfig, Keys, Logger, util_functions as uf, Config

from qrogue.graphics.widgets import Renderable


class MyBaseWidget(BlockLabel):
    def __init__(self, wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger):
        super().__init__(wid, title, grid, row, column, row_span, column_span, padx, pady, center, logger)

    def set_title(self, title: str) -> None:
        super(MyBaseWidget, self).set_title(title)

    def get_title(self) -> str:
        return super(MyBaseWidget, self).get_title()

    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = [0,1], include_whitespace: bool=False, selected_color=None) -> None:
        super(MyBaseWidget, self).add_text_color_rule(regex, color, rule_type, match_type, region, include_whitespace,
                                                      selected_color)

    def add_key_command(self, keys: List[int], command: Callable[[],Any]) -> Any:
        for key in keys:
            super(MyBaseWidget, self).add_key_command(key, command)


class Widget(Renderable, ABC):
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
        if self.__map_name:
            text += f"{self.__map_name}\t"
        if self.__robot:
            text += f"{self.__robot.cur_hp} / {self.__robot.max_hp} HP   \t" \
                   f"{self.__robot.backpack.coin_count}$, {self.__robot.key_count()} keys"
        if self.__render_duration:
            text += f"\t\t{self.__render_duration:.2f} ms"
        self.widget.set_title(text)

    def render_reset(self) -> None:
        self.widget.set_title("")


class CircuitWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__robot = None
        # highlight everything between {} (gates), |> (start) or <| (end)
        widget.add_text_color_rule("(\{.*?\}|\|.*?\>|\<.*?\|)", ColorConfig.CIRCUIT_COLOR, 'contains',
                                   match_type='regex')

    def set_data(self, robot: Robot) -> None:
        self.__robot = robot

    def render(self) -> None:
        if self.__robot is not None:
            entry = "-" * (3 + InstructionConfig.MAX_ABBREVIATION_LEN + 3)
            rows = [[entry] * self.__robot.circuit_space for _ in range(self.__robot.num_of_qubits)]

            for i, inst in self.__robot.circuit_enumerator():
                for q in inst.qargs_iter():
                    inst_str = inst.abbreviation(q)
                    diff_len = InstructionConfig.MAX_ABBREVIATION_LEN - len(inst_str)
                    inst_str = f"--{{{inst_str}}}--"
                    if diff_len > 0:
                        half_diff = int(diff_len / 2)
                        inst_str = inst_str.ljust(len(inst_str) + half_diff, "-")
                        if diff_len % 2 == 0:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff, "-")
                        else:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff + 1, "-")
                    rows[q][i] = inst_str
            circ_str = ""
            # place qubits from top to bottom, high to low index
            for q in range(len(rows) - 1, -1, -1):
                circ_str += f"| q{q} >---"
                row = rows[q]
                for i in range(len(row)):
                    circ_str += row[i]
                    if i < len(row) - 1:
                         circ_str += "+"
                circ_str += "< out |\n"
            self.widget.set_title(circ_str)

    def render_reset(self) -> None:
        self.widget.set_title("")


class MapWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__map = None
        self.__backup = None

    def set_data(self, map: Map) -> None:
        self.__map = map

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


class TargetStateVectorWidget(Widget):
    def __init__(self, widget: MyBaseWidget, headline: str):
        super().__init__(widget)
        self.__headline = headline
        self.__state_vector_str = None
        widget.add_text_color_rule("~.*~", ColorConfig.STV_HEADING_COLOR, 'contains', match_type='regex')

    def set_data(self, state_vector_str: str) -> None:
        self.__state_vector_str = state_vector_str

    def render(self) -> None:
        if self.__state_vector_str:
            str_rep = f"~{self.__headline}~\n{self.__state_vector_str}"
            self.widget.set_title(str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")


class CurrentStateVectorWidget(Widget):
    def __init__(self, widget: MyBaseWidget, headline: str):
        super().__init__(widget)
        self.__headline = headline
        self.__state_vector_str = None
        self.__diff_vector_str = None
        widget.add_text_color_rule("~.*~", ColorConfig.STV_HEADING_COLOR, 'contains', match_type='regex')
        widget.add_text_color_rule("\(0\)", ColorConfig.CORRECT_AMPLITUDE_COLOR, "contains", match_type="regex")
        #widget.add_text_color_rule("\(\d\)", ColorConfig.CORRECT_AMPLITUDE_COLOR, "contains", match_type="regex")
        widget.add_text_color_rule("\([^0].*\)", ColorConfig.WRONG_AMPLITUDE_COLOR, "contains", match_type="regex")

    def set_data(self, state_vector_strings: Tuple[str, str]) -> None:
        self.__state_vector_str, self.__diff_vector_str = state_vector_strings

    def render(self) -> None:
        if self.__state_vector_str is not None:
            str_rep = f"~{self.__headline}~\n"
            stv_rows = self.__state_vector_str.split('\n')
            diff_rows = ["(" + val + ")" for val in self.__diff_vector_str.split('\n')]

            max_stv_width = max([len(val) for val in stv_rows])
            max_diff_width = max([len(val) for val in diff_rows])

            # last row is empty due to the trailing \n and therefore uninteresting to us
            for i in range(len(stv_rows) - 1):
                str_rep += uf.center_string(stv_rows[i], max_stv_width, uneven_left=True)
                str_rep += "  "
                str_rep += uf.center_string(diff_rows[i], max_diff_width, uneven_left=False)
                str_rep += "\n"
            self.widget.set_title(str_rep)

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
                row = row[::-1] # [::-1] reverses the list so q0 is on the left
            body += box_left + row + box_right
            body += "\n"

        self.__text = head + "\n" + body
        self.widget.set_title(self.__text)

    def render(self) -> None:
        #self.widget.set_title(self.__text)
        pass

    def render_reset(self) -> None:
        self.widget.set_title("")


class SelectionWidget(Widget):
    __COLUMN_SEPARATOR = "   "

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
        self.widget.add_key_command(hotkeys[indices[0]], lambda : self.__jump_to_index(indices[0]))
        self.widget.add_key_command(hotkeys[indices[1]], lambda : self.__jump_to_index(indices[1]))
        self.widget.add_key_command(hotkeys[indices[2]], lambda : self.__jump_to_index(indices[2]))
        self.widget.add_key_command(hotkeys[indices[3]], lambda : self.__jump_to_index(indices[3]))
        self.widget.add_key_command(hotkeys[indices[4]], lambda : self.__jump_to_index(indices[4]))
        self.widget.add_key_command(hotkeys[indices[5]], lambda : self.__jump_to_index(indices[5]))
        self.widget.add_key_command(hotkeys[indices[6]], lambda : self.__jump_to_index(indices[6]))
        self.widget.add_key_command(hotkeys[indices[7]], lambda : self.__jump_to_index(indices[7]))
        self.widget.add_key_command(hotkeys[indices[8]], lambda : self.__jump_to_index(indices[8]))
        self.widget.add_key_command(hotkeys[indices[9]], lambda : self.__jump_to_index(indices[9]))

    @property
    def num_of_choices(self) -> int:
        return len(self.__choices)

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
        str_rep = ""
        for i in range(self.num_of_choices):
            if i == self.__index and (self.widget.is_selected() or self.__stay_selected):
                wrapper = "-> "
            else:
                wrapper = "   "
            str_rep += wrapper
            str_rep += self.__choices[i]
            str_rep += " "
            if i % self.__columns == self.__columns - 1:
                str_rep += "\n"
            else:
                str_rep += self.__COLUMN_SEPARATOR
        self.widget.set_title(str_rep)

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

    def up(self) -> None:
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

    def right(self) -> None:
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

    def down(self) -> None:
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

    def left(self) -> None:
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
        if ret is None: # move focus if nothing is returned
            return True
        else:
            return ret
