from typing import Callable, Tuple, List, Optional

from py_cui import ColorRule
from py_cui.popups import Popup as PyCuiPopup
from py_cui.ui import MenuImplementation

from qrogue.util import ColorConfig as CC, Keys, Logger, PopupConfig, ColorConfig, ColorCode


class MultilinePopup(PyCuiPopup, MenuImplementation):
    __STATIC_PY_CUI_PADDING = 6     # based on PyCUI "padding" I think
    __QUESTION_SPACING = " " * 7
    __QUESTION_ARROW = "-->"
    __QUESTION_SELECTION = " " * (len(__QUESTION_SPACING) - (len(__QUESTION_ARROW) + 1)) + (__QUESTION_ARROW + " ")

    @staticmethod
    def __get_color_rules():
        regex = CC.REGEX_TEXT_HIGHLIGHT
        return [
            ColorRule(f"{regex}.*?{regex}", 0, 0, "contains", "regex", [0, 1],
                      False, Logger.instance()),
            ColorRule(MultilinePopup.__QUESTION_ARROW, ColorConfig.QUESTION_SELECTION_COLOR, 0, "contains", "regex",
                      [0, 1], False, Logger.instance()),
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
                 confirmation_callback: Callable[[int], None] = None, answers: Optional[List] = None,
                 pos: Optional[Tuple[int, int]] = None, dimensions: Optional[Tuple[int, int]] = None,
                 situational_callback: Optional[Tuple[Optional[Callable[[], None]], Optional[Callable[[], None]]]] =
                 None):
        # custom_size needs to be initialized immediately because get_absolute_stop_pos() in init() accesses it
        self.__custom_size = False

        super().__init__(root, title, text, color, renderer, logger)
        self.__controls = controls
        self.__confirmation_callback = confirmation_callback
        if answers is None and self._is_question:
            self.__answers = ["Confirm", "Cancel"]
        else:
            self.__answers = answers

        if pos is not None:
            if pos[0] is not None:
                self._start_x = pos[0]
            if pos[1] is not None:
                self._start_y = pos[1]

        if dimensions is not None:
            self.__custom_size = True
            self._height, self._width = dimensions
            self._stop_x, self._stop_y = self._start_x + self._width, self._start_y + self._height

        def _dummy():
            pass
        self.__situational_callback1 = _dummy
        self.__situational_callback2 = _dummy
        if situational_callback is not None:
            sit1, sit2 = situational_callback
            if sit1 is not None: self.__situational_callback1 = sit1
            if sit2 is not None: self.__situational_callback2 = sit2

        self._top_view = 0
        self.__lines = MultilinePopup.__split_text(text, self._width - MultilinePopup.__STATIC_PY_CUI_PADDING,
                                                   PopupConfig.PADDING_X, logger)

        self.__question_state = 0
        self._pageAlignment = " " * (self._width - MultilinePopup.__STATIC_PY_CUI_PADDING)

    @property
    def _is_question(self) -> bool:
        return self.__confirmation_callback is not None

    @property
    def textbox_height(self) -> int:
        """

        :return: number of rows inside the popup
        """
        full_page_height = self._height - self._pady - 2    # subtract both title and end line
        if self._is_question:
            full_page_height -= 2   # subtract the two lines needed for answer selection
        if len(self.__lines) > full_page_height:
            return full_page_height - 1     # subtract the space we need for page indication
        return full_page_height

    def __up(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view -= 1

    def __down_fast(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view = max(self._top_view - self.textbox_height, 0)

    def __down(self):
        # since _top_view can never be negative we don't need to check if we have lines that don't fit on the popup
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view += 1

    def __up_fast(self):
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view = min(self._top_view + self.textbox_height, len(self.__lines) - self.textbox_height)

    def _handle_key_press(self, key_pressed):
        """Overrides base class handle_key_press function
        """
        # regarding the idea to move this functionality to Keys.PopupLeft and Keys.PopupRight:
        # these keys should definitely be used for selecting the answer in question popups, so it would only make it
        # more inconsistent and confusing im question popups and classical popups have different keys for, e.g.,
        # navigating through history
        if key_pressed in self.__controls.get_keys(Keys.Situational1):
            self.__situational_callback1()
        elif key_pressed in self.__controls.get_keys(Keys.Situational2):
            self.__situational_callback2()

        elif self._is_question:
            if key_pressed in self.__controls.get_keys(Keys.Action):
                self.__confirmation_callback(self.__question_state)
                self._root.close_popup()
            elif key_pressed in self.__controls.get_keys(Keys.PopupRight):
                self.__question_state = min(self.__question_state + 1, len(self.__answers) - 1)
            elif key_pressed in self.__controls.get_keys(Keys.PopupLeft):
                self.__question_state = max(self.__question_state - 1, 0)
            elif key_pressed in self.__controls.get_keys(Keys.PopupUp):
                self.__up()
            elif key_pressed in self.__controls.get_keys(Keys.PopupDown):
                self.__down()
        else:
            if key_pressed in self.__controls.get_keys(Keys.PopupClose):
                self._root.close_popup()
            elif key_pressed in self.__controls.get_keys(Keys.PopupUp):
                self.__up()
            elif key_pressed in self.__controls.get_keys(Keys.PopupLeft):
                self.__up_fast()
            elif key_pressed in self.__controls.get_keys(Keys.PopupDown):
                self.__down()
            elif key_pressed in self.__controls.get_keys(Keys.PopupRight):
                self.__down_fast()

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

        info_line_y = self._start_y + self.textbox_height + 1
        if len(self.__lines) > self.textbox_height:
            rem_rows = str(len(self.__lines) - counter - self._top_view + 1)
            rem_rows = self._pageAlignment[:-len(rem_rows)] + ColorConfig.colorize(ColorCode.POPUP_META_INFO, rem_rows)
            prefix = PopupConfig.scroll_indicator()
            rem_rows = ColorConfig.colorize(ColorCode.POPUP_META_INFO, prefix) + rem_rows[len(prefix):]
            self._renderer.draw_text(self, rem_rows, info_line_y, selected=False)
            info_line_y += 1

        if self._is_question:
            # the question answers should always be positioned at the very bottom of the popup
            self._renderer.draw_text(self, "-" * self._width, info_line_y, selected=True)

            text = ""
            for i in range(len(self.__answers)):
                if i == self.__question_state:
                    text += MultilinePopup.__QUESTION_SELECTION
                else:
                    text += MultilinePopup.__QUESTION_SPACING
                text += self.__answers[i]
            self._renderer.draw_text(self, text, info_line_y + 1, selected=False)

        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)

    def get_absolute_stop_pos(self) -> Tuple[int, int]:
        # override for custom sizes, so we can calculate the stop position based on our custom width and height instead
        # of calculating width and height based on start and stop
        if self.__custom_size:
            start_x, start_y = self.get_absolute_start_pos()
            self._stop_x, self._stop_y = start_x + self._width, start_y + self._height
            return self._stop_x, self._stop_y
        else:
            return super(MultilinePopup, self).get_absolute_stop_pos()

    def freeze(self):
        """
        The popup will be normalized to have the default size and position. Additionally, questions are transformed into
        statements with the current answer being the final/saved answer.
        """
        if self._is_question:
            # without a confirmation_callback the popup is not regarded as questions and hence the answer cannot change
            self.__confirmation_callback = None
        self.__custom_size = False
        self._start_x, self._start_y = self.get_absolute_start_pos()    # returns the default start position (56, 11)
