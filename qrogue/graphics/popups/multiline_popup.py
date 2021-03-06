from typing import Callable, Tuple, List

from py_cui import ColorRule
from py_cui.popups import Popup as PyCuiPopup
from py_cui.ui import MenuImplementation

from qrogue.util import ColorConfig as CC, Keys, Logger, PopupConfig


class MultilinePopup(PyCuiPopup, MenuImplementation):
    @staticmethod
    def __get_color_rules():
        regex = CC.REGEX_TEXT_HIGHLIGHT
        return [
            ColorRule(f"{regex}.*?{regex}", 0, 0, "contains", "regex", [0, 1],
                      False, Logger.instance())
        ]

    @staticmethod
    def __split_text(text: str, width: int, padding: int, logger) -> List[str]:
        """

        :param text: text to split into multiple lines
        :param width: the maximum width of one line
        :param padding: how much spaces we should place at the start and end of each line
        :return: list of text parts with a maximum of #width characters
        """
        width -= padding * 2    # remove the space needed for padding
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
        return [" " * padding + line + " " * padding for line in split_text]

    def __init__(self, root, title, text, color, renderer, logger, controls,
                 confirmation_callback: Callable[[bool], None] = None, pos: Tuple[int, int] = None):
        super().__init__(root, title, text, color, renderer, logger)
        self.__controls = controls
        self.__confirmation_callback = confirmation_callback
        self._top_view = 0

        #self._pady = PopupConfig.PADDING_Y
        self.__lines = MultilinePopup.__split_text(text, self._width - 6, PopupConfig.PADDING_X, logger)  # 6: based on PyCUI "padding" I think

        if pos:
            if pos[0] is not None:
                self._start_x = pos[0]
            if pos[1] is not None:
                self._start_y = pos[1]

        if self._is_question:
            self.__lines.append("-" * self._width + "\n")
            self.__lines.append("Cancel" + " " * 10 + "Confirm")     # todo how to explain controls?

    @property
    def _is_question(self) -> bool:
        return self.__confirmation_callback is not None

    @property
    def textbox_height(self) -> int:
        """

        :return: number of rows inside the popup
        """
        return self._height - self._pady - 2    # subtract both title and end line

    def up(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view -= 1

    def down_fast(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view = max(self._top_view - self.textbox_height, 0)

    def down(self):
        # since _top_view can never be negative we don't need to check if we have lines that don't fit on the popup
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view += 1

    def up_fast(self):
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view = min(self._top_view + self.textbox_height, len(self.__lines) - self.textbox_height)

    def _handle_key_press(self, key_pressed):
        """Overrides base class handle_key_press function
        """
        if self._is_question:
            if key_pressed in self.__controls.get_keys(Keys.Action):
                self.__confirmation_callback(True)
                self._root.close_popup()
            elif key_pressed in self.__controls.get_keys(Keys.Cancel):
                self.__confirmation_callback(False)
                self._root.close_popup()
        else:
            if key_pressed in self.__controls.get_keys(Keys.PopupClose):
                self._root.close_popup()
            elif key_pressed in self.__controls.get_keys(Keys.PopupScrollUp):
                self.up()
            elif key_pressed in self.__controls.get_keys(Keys.PopupScrollUpFast):
                self.up_fast()
            elif key_pressed in self.__controls.get_keys(Keys.PopupScrollDown):
                self.down()
            elif key_pressed in self.__controls.get_keys(Keys.PopupScrollDownFast):
                self.down_fast()

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
