from enum import Enum

import py_cui
import py_cui.ui
from py_cui import ColorRule

from util.config import PopupConfig, ColorConfig as CC
from util.logger import Logger


class Popup:
    __show_popup = None

    @staticmethod
    def update_popup_functions(show_popup_callback: "void(str, str, int)") -> None:
        Popup.__show_popup = show_popup_callback

    @staticmethod
    def show_popup() -> "void(str, str, int)":
        return Popup.__show_popup

    @staticmethod
    def message(title: str, text: str, color: int = PopupConfig.default_color()):
        Popup(title, text, color, show=True)

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color(), show: bool = True):
        self.__title = title
        self.__text = text
        self.__color = color
        if show:
            self.show()

    def show(self, show_popup_callback: "void(str, str, int)" = None) -> None:
        if show_popup_callback is None:
            Popup.__show_popup(self.__title, self.__text, self.__color)
        else:
            show_popup_callback(self.__title, self.__text, self.__color)


class MultilinePopup(py_cui.popups.Popup, py_cui.ui.MenuImplementation):
    @staticmethod
    def __get_color_rules():
        regex = CC.REGEX_TEXT_HIGHLIGHT
        return [
            ColorRule(f"{regex}.*?{regex}", 0, 0, "contains", "regex", [0, 1],
                      False, Logger.instance())
        ]

    @staticmethod
    def __split_text(text: str, width: int, logger) -> "list of str":
        """

        :param text: text to split into multiple lines
        :param width: the maximum width of one line
        :return: list of text parts with a maximum of #width characters
        """
        split_text = []
        for paragraph in text.splitlines():
            index = 0
            prepend = None
            while index + width < len(paragraph):
                cur_part = paragraph[index:]
                # check if the previous line ended with a color rule and prepend it
                if prepend:
                    prev_len = len(cur_part)
                    cur_part = prepend + cur_part.lstrip()
                    # we have to adapt the index since we potentially remove whitespace in front and therefore have
                    # the possibility of a longer line which leads to a higher increment of the index and furthermore
                    # to the potential loss of some characters in the beginning of the new_line
                    # prepend also needs to be part of this adaption because it will be counted in character_removals
                    index -= (len(cur_part) - prev_len)
                    prepend = None
                character_removals = CC.count_meta_characters(cur_part, width, logger)

                last_whitespace = cur_part.rfind(" ", 1, width + character_removals)
                if last_whitespace == -1:
                    cur_width = width + character_removals
                else:
                    cur_width = last_whitespace

                next_line = cur_part[:cur_width].lstrip()
                if len(next_line) > 0:
                    # check if next_line ends with an un-terminated color rule
                    last_highlight = next_line.rfind(CC.TEXT_HIGHLIGHT)
                    if 0 <= last_highlight < len(next_line) - CC.HIGHLIGHT_WIDTH:
                        # if so, terminate it and remember to continue it in the next line
                        code_start = last_highlight + CC.HIGHLIGHT_WIDTH
                        # TODO a highlighted number can potentially lead to problems here! (at least theoretically,
                        # todo but somehow I couldn't produce a breaking example so I might be wrong)
                        # todo also if we place an at-least-2-digits number directly after a highlight
                        if CC.is_number(next_line[code_start:code_start + CC.CODE_WIDTH]):
                            next_line += CC.TEXT_HIGHLIGHT
                            prepend = next_line[last_highlight:code_start + CC.CODE_WIDTH]
                    split_text.append(next_line)
                index += cur_width

            # The last line is appended as it is (maybe with additional color rule prepend from the previous line)
            if prepend:
                split_text.append(prepend + paragraph[index:].strip())
            else:
                split_text.append(paragraph[index:].strip())
        return split_text

    def __init__(self, root, title, text, color, renderer, logger, controls):
        super().__init__(root, title, text, color, renderer, logger)
        self.__controls = controls
        self._top_view = 0
        self.__lines = MultilinePopup.__split_text(text, self._width - 6, logger)  # 6: based on PyCUI "padding" I think

    @property
    def textbox_height(self) -> int:
        return self._height - self._pady - 2    # subtract both title and end line

    def up(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view -= 1

    def down(self):
        # since _top_view can never be negative we don't need to check if we have lines that don't fit on the popup
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view += 1

    def _handle_key_press(self, key_pressed):
        """Overrides base class handle_key_press function
        """
        if key_pressed in self.__controls.popup_close:
            self._root.close_popup()
        elif key_pressed == self.__controls.popup_scroll_up:
            self.up()
        elif key_pressed == self.__controls.popup_scroll_down:
            self.down()

    def _draw(self):
        """Overrides base class draw function
        """

        self._renderer.set_color_mode(self._color)
        self._renderer.draw_border(self)
        self._renderer.set_color_rules(self.__get_color_rules())
        counter = self._pady + 1
        for i in range(self._top_view, len(self.__lines)):
            if counter > self.textbox_height:
                break
            self._renderer.draw_text(self, self.__lines[i], self._start_y + counter, selected=True)
            counter += 1
            i += 1
        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)


def _locked_door() -> str:
    key = CC.highlight_object("Key")
    door = CC.highlight_object("Door")
    return f"Come back with a {key} to open the {door}."
def _entangled_door() -> str:
    door = CC.highlight_object("Door")
    entangled = CC.highlight_word("entangled")
    return f"The {door} {entangled} with this one was opened. Therefore you can no longer pass this {door}."
def _tutorial_blocked() -> str:
    step = CC.highlight_word("current step")
    tutorial = CC.highlight_word("Tutorial")
    return f"You should not go there yet! Finish the {step} of the {tutorial} first."
def _not_enough_money() -> str:
    return "You cannot afford that right now. Come back when you have enough money."
def _no_space() -> str:
    circ = CC.highlight_object("Circuit")
    space = CC.highlight_word("no more space")
    gate = CC.highlight_object("Gate")
    return f"Your {circ} has {space} left. Remove a {gate} to place another one."
class CommonPopups(Enum):
    LockedDoor = ("Door is locked!", _locked_door())
    EntangledDoor = ("Door is entangled!", _entangled_door())
    TutorialBlocked = ("Halt!", _tutorial_blocked())
    NotEnoughMoney = ("$$$", _not_enough_money())
    NoCircuitSpace = ("Nope", _no_space())

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color()):
        self.__title = title
        self.__text = text
        self.__color = color

    def show(self):
        Popup.message(self.__title, self.__text, self.__color)
