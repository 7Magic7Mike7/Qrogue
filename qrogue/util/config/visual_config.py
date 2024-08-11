import enum
import math
from typing import Optional, Tuple, List, Callable, Dict

from qrogue.util.config.py_cui_config import PyCuiColors


class ColorCode(enum.Enum):
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    ACTION_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
    WORD_HIGHLIGHT = "05"

    INV_TILE_HIGHLIGHT = "11"
    INV_OBJECT_HIGHLIGHT = "12"
    INV_ACTION_HIGHLIGHT = "13"
    INV_KEY_HIGHLIGHT = "14"
    INV_WORD_HIGHLIGHT = "15"

    POPUP_META_INFO = "20"

    PUZZLE_WRONG_AMPLITUDE = "90"
    PUZZLE_CORRECT_AMPLITUDE = "91"
    PUZZLE_HEADLINES = "92"
    PUZZLE_KET = "93"

    def __init__(self, code: str):
        self.__code = code

    def __str__(self):
        return self.__code


class ColorConfig:
    CODE_WIDTH = 2
    SELECTION_COLOR = PyCuiColors.BLACK_ON_WHITE
    QUBIT_INFO_COLOR = PyCuiColors.CYAN_ON_BLACK
    QUBIT_CONFIG_COLOR = PyCuiColors.YELLOW_ON_BLACK
    STV_HEADING_COLOR = PyCuiColors.CYAN_ON_BLACK
    CIRCUIT_COLOR = PyCuiColors.MAGENTA_ON_BLACK
    CIRCUIT_LABEL_COLOR = PyCuiColors.CYAN_ON_BLACK
    QUESTION_SELECTION_COLOR = PyCuiColors.WHITE_ON_BLACK
    LEVEL_SELECTION_HEADER_COLOR = PyCuiColors.CYAN_ON_BLACK
    SEED_INPUT_POPUP_COLOR = PyCuiColors.BLACK_ON_WHITE
    LEVEL_SELECTION_INPUT_MAP_CODE = PyCuiColors.RED_ON_BLACK
    FUSION_CIRCUIT_NAMING_COLOR = PyCuiColors.BLACK_ON_WHITE

    ERROR_COLOR = PyCuiColors.RED_ON_BLUE
    TEXT_HIGHLIGHT = "//"
    REGEX_TEXT_HIGHLIGHT = "//"  # regex recognizable version of TEXT_HIGHLIGHT (some characters need escaping)
    HIGHLIGHT_WIDTH = len(TEXT_HIGHLIGHT)
    __DIC = {
        str(ColorCode.TILE_HIGHLIGHT):      PyCuiColors.WHITE_ON_BLACK,
        str(ColorCode.OBJECT_HIGHLIGHT):    PyCuiColors.GREEN_ON_WHITE,
        str(ColorCode.ACTION_HIGHLIGHT):    PyCuiColors.RED_ON_WHITE,
        str(ColorCode.KEY_HIGHLIGHT):       PyCuiColors.MAGENTA_ON_WHITE,
        str(ColorCode.WORD_HIGHLIGHT):      PyCuiColors.BLUE_ON_WHITE,

        str(ColorCode.INV_TILE_HIGHLIGHT):      PyCuiColors.BLACK_ON_WHITE,
        str(ColorCode.INV_OBJECT_HIGHLIGHT):    PyCuiColors.GREEN_ON_BLACK,
        str(ColorCode.INV_ACTION_HIGHLIGHT):    PyCuiColors.RED_ON_BLACK,
        str(ColorCode.INV_KEY_HIGHLIGHT):       PyCuiColors.MAGENTA_ON_BLACK,
        str(ColorCode.INV_WORD_HIGHLIGHT):      PyCuiColors.BLUE_ON_BLACK,

        str(ColorCode.POPUP_META_INFO):         PyCuiColors.WHITE_ON_MAGENTA,

        str(ColorCode.PUZZLE_WRONG_AMPLITUDE):      PyCuiColors.RED_ON_BLACK,
        str(ColorCode.PUZZLE_CORRECT_AMPLITUDE):    PyCuiColors.GREEN_ON_BLACK,
        str(ColorCode.PUZZLE_HEADLINES):            STV_HEADING_COLOR,
        str(ColorCode.PUZZLE_KET):                  QUBIT_CONFIG_COLOR,
    }

    @staticmethod
    def is_number(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_punctuation(char: str) -> bool:
        return char in [".", ",", "!", "?", ":", "\""]

    @staticmethod
    def __find(paragraph: str, start: int, end: int) -> int:
        # adapt end because meta characters are not printed and therefore they can be directly after end
        end += ColorConfig.HIGHLIGHT_WIDTH - 1
        return paragraph.find(ColorConfig.TEXT_HIGHLIGHT, start, end)

    @staticmethod
    def count_meta_characters(paragraph: str, width: int, handle_error: Callable[[str], None]) -> int:
        """
        Counts how many meta characters (i.e. not printed characters) there are in the first #width characters of
        paragraph. This way we know for example by how much we can extend the rendered text since these characters
        won't be rendered.

        :param paragraph: the str we won't to count the number of meta characters for
        :param width: number of characters we consider in paragraph (i.e. line width)
        :param handle_error: handles potential errors
        :return: number of found meta characters
        """
        character_removals = 0
        # check how many meta-characters (indicating color rules) we have in our line
        highlight_index = ColorConfig.__find(paragraph, 0, width)
        start = True  # whether we search for the start of a highlighted section or an end
        while highlight_index > -1:
            highlight_index += ColorConfig.HIGHLIGHT_WIDTH
            if start:
                if highlight_index + ColorConfig.CODE_WIDTH <= len(paragraph) and \
                        ColorConfig.is_number(paragraph[highlight_index:highlight_index + ColorConfig.CODE_WIDTH]):
                    last_whitespace = paragraph.rfind(" ", highlight_index,
                                                      width + character_removals + 1 + ColorConfig.CODE_WIDTH)
                    if last_whitespace > -1:
                        character_removals += ColorConfig.HIGHLIGHT_WIDTH + ColorConfig.CODE_WIDTH
                        start = False
                    elif paragraph.endswith(ColorConfig.TEXT_HIGHLIGHT):
                        # due to splitting a line in the middle of a color rule it can happen that there is no " "
                        # at the end but a "/" and therefore it would still fit
                        character_removals += ColorConfig.HIGHLIGHT_WIDTH + ColorConfig.CODE_WIDTH \
                                              + ColorConfig.HIGHLIGHT_WIDTH
                        break
                    elif ColorConfig.is_punctuation(paragraph[-1]):
                        # TODO I don't think -1 is correct, because it is the very end, but somehow it works
                        # if the very last word is highlighted we also have no whitespace at the end
                        character_removals += ColorConfig.HIGHLIGHT_WIDTH + ColorConfig.CODE_WIDTH \
                                              + ColorConfig.HIGHLIGHT_WIDTH
                        break
                    else:
                        break
                else:
                    handle_error(f"Illegal start index = {highlight_index} for \"{paragraph}\". Make sure no text"
                                 f" contains \"{ColorConfig.TEXT_HIGHLIGHT}\" or a 2 or more digit number directly"
                                 f" after a highlighting (space in-between is okay)!")
            else:
                character_removals += ColorConfig.HIGHLIGHT_WIDTH
                start = True
            highlight_index = ColorConfig.__find(paragraph, highlight_index, width + character_removals)
        return character_removals

    @staticmethod
    def colorize(color_code: ColorCode, text) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{color_code}{text}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_tile(tile: str, invert: bool = False) -> str:
        """
        Highlights tile strings.
        :param tile: a string to highlight as tile
        :param invert: whether to use the normal or inverted background colors
        :return:
        """
        if invert:
            return ColorConfig.colorize(ColorCode.INV_TILE_HIGHLIGHT, tile)
        else:
            return ColorConfig.colorize(ColorCode.TILE_HIGHLIGHT, tile)

    @staticmethod
    def highlight_object(obj: str, invert: bool = False) -> str:
        """
        Highlights something directly gameplay related. I.e. things you encounter in the game.
        :param obj: a string to highlight as object
        :param invert: whether to use the normal or inverted background colors
        :return:
        """
        if invert:
            return ColorConfig.colorize(ColorCode.INV_OBJECT_HIGHLIGHT, obj)
        else:
            return ColorConfig.colorize(ColorCode.OBJECT_HIGHLIGHT, obj)

    @staticmethod
    def highlight_action(action: str, invert: bool = False) -> str:
        """
        Highlights action words that explain what you can do in the game.
        :param action: a string to highlight as action
        :param invert: whether to use the normal or inverted background colors
        :return:
        """
        if invert:
            return ColorConfig.colorize(ColorCode.INV_ACTION_HIGHLIGHT, action)
        else:
            return ColorConfig.colorize(ColorCode.ACTION_HIGHLIGHT, action)

    @staticmethod
    def highlight_key(key: str, invert: bool = False) -> str:
        """
        Highlights a keyboard input.
        :param key: a string to highlight as key
        :param invert: whether to use the normal or inverted background colors
        :return:
        """
        if invert:
            return ColorConfig.colorize(ColorCode.INV_KEY_HIGHLIGHT, key)
        else:
            return ColorConfig.colorize(ColorCode.KEY_HIGHLIGHT, key)

    @staticmethod
    def highlight_word(word: str, invert: bool = False) -> str:
        """
        Highlights miscellaneous words that should be highlighted.
        :param word: a string to highlight as important word
        :param invert: whether to use the normal or inverted background colors
        :return:
        """
        if invert:
            return ColorConfig.colorize(ColorCode.INV_WORD_HIGHLIGHT, word)
        else:
            return ColorConfig.colorize(ColorCode.WORD_HIGHLIGHT, word)

    @staticmethod
    def get(char: str) -> int:
        try:
            return ColorConfig.__DIC[char]
        except KeyError:
            return ColorConfig.ERROR_COLOR

    @staticmethod
    def get_from_code(code: ColorCode) -> int:
        return ColorConfig.get(str(code))


class PopupConfig:
    class Importance(enum.IntEnum):
        Undefined = 0
        Dialogue = 1
        Info = 2
        Error = 3

        @staticmethod
        def from_int(value: int) -> "PopupConfig.Importance":
            if value == PopupConfig.Importance.Dialogue: return PopupConfig.Importance.Dialogue
            if value == PopupConfig.Importance.Info: return PopupConfig.Importance.Info
            if value == PopupConfig.Importance.Error: return PopupConfig.Importance.Error
            return PopupConfig.Importance.Undefined

    # note that the metric is:
    # 0=Center, >0 = distance to left or top border, <0 = distance to right or bottom border
    __DEFAULT_POSITION = 0
    __CENTER_POS = 0    # special number to indicate the center
    __TOP_POS = 3       # three rows below top
    __RIGHT_POS = -5    # five columns left of right
    __BOT_POS = -3      # three rows above bot
    __LEFT_POS = 5      # five columns right of left
    # just a very large number that we definitely won't use for regular positions to indicate +0 and -0:
    __ZERO_POS = 1_000_000
    __POSITIONS = [  # None = center
        (__CENTER_POS, __CENTER_POS), (__CENTER_POS, __TOP_POS), (__RIGHT_POS, __TOP_POS), (__RIGHT_POS, __CENTER_POS),
        (__RIGHT_POS, __BOT_POS), (__CENTER_POS, __BOT_POS), (__LEFT_POS, __BOT_POS), (__LEFT_POS, __CENTER_POS),
        (__LEFT_POS, __TOP_POS),
        # special handcrafted positions
        (+__ZERO_POS, 6),  # for matrix popup on top of normal matrix widget
    ]
    __INDEX_X = 0  # position of X in position tuple
    __INDEX_Y = 1  # position of Y in position tuple

    PADDING_X = 2
    PADDING_Y = 2

    @staticmethod
    def scroll_indicator() -> str:
        return "scroll down"

    @staticmethod
    def default_color() -> int:
        return PyCuiColors.BLACK_ON_WHITE

    @staticmethod
    def default_position() -> int:
        assert 0 <= PopupConfig.__DEFAULT_POSITION < len(PopupConfig.__POSITIONS), "Invalid DefaultPosition for Popups!"
        return PopupConfig.__DEFAULT_POSITION

    @staticmethod
    def __resolve_pos_val(pos: int, val_index: int) -> Tuple[Optional[bool], int]:
        """

        Args:
            pos: position indicated via index in internal __POSITIONS list
            val_index: index of the value in the position tuple

        Returns: A tuple indicating the reference position (left or up=True, right or bottom=False, center=None) and
        the distance of the indexed value to its reference position. E.g., a position near the bottom right corner could
        return (False, 3), meaning its either 3 rows (if val_index corresponds to y-position) above the bottom of the
        window or 3 columns (if val_index corresponds to x-position) to the left of the right end of the window.

        """
        if 0 <= pos < len(PopupConfig.__POSITIONS):
            val = PopupConfig.__POSITIONS[pos][val_index]
            if val == +PopupConfig.__ZERO_POS: return True, 0
            if val == -PopupConfig.__ZERO_POS: return False, 0
            if val > 0: return True, val
            if val < 0: return False, -val  # since we return a distance, the value needs to be positive
            return None, 0  # val must be "normal" 0 (or None corresponding to 0)
        else:
            return PopupConfig.__resolve_pos_val(PopupConfig.default_position(), val_index)

    @staticmethod
    def resolve_position_x(pos: int) -> Tuple[Optional[bool], int]:
        """

        Args:
            pos: position indicated via index in internal __POSITIONS list

        Returns: A tuple indicating the reference position (left=True, right=False, center=None) and the x-distance to
        the reference position. E.g., a position near the bottom right corner could return (False, 3), meaning its 3
        columns to the left of the right end of the window.

        """
        return PopupConfig.__resolve_pos_val(pos, PopupConfig.__INDEX_X)

    @staticmethod
    def resolve_position_y(pos: int) -> Tuple[Optional[bool], int]:
        """

        Args:
            pos: position indicated via index in internal __POSITIONS list

        Returns: A tuple indicating the reference position (top=True, bottom=False, center=None) and the y-distance to
        the reference position. E.g., a position near the bottom right corner could return (False, 3), meaning its 3
        rows above the bottom of the window.

        """
        return PopupConfig.__resolve_pos_val(pos, PopupConfig.__INDEX_Y)


class UIConfig:
    class Dimensions:
        @staticmethod
        def __from_margins(margin_left: int, margin_top: int, center_x: bool = True, center_y: bool = False,
                           pad_x: Optional[int] = None, pad_y: Optional[int] = None):
            # NOT FULLY WORKING I THINK
            if margin_left < 0 and not center_x:
                width = UIConfig.WINDOW_WIDTH + margin_left
                margin_left = 0     # it's 0 since we place it from the right
            else:
                # if margin_left > 0: nothing changes; else we want to center anyways and can place from the left
                margin_left = abs(margin_left)
                width = UIConfig.WINDOW_WIDTH - margin_left
                if center_x: width -= margin_left  # subtract an additional time for the other side

            if margin_top < 0 and not center_y:
                height = UIConfig.WINDOW_HEIGHT + margin_top
                margin_top = 0
            else:
                abs_margin_top = abs(margin_top)
                height = UIConfig.WINDOW_HEIGHT-abs_margin_top
                if center_y: height -= abs_margin_top   # subtract an additional time for the other side

            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def __init__(self, width: int, height: int, margin_left: Optional[int] = None, margin_top: Optional[int] = None,
                     pad_x: Optional[int] = None, pad_y: Optional[int] = None):
            # check for 0 and relative 0 if using negative values
            assert width not in (0, -UIConfig.WINDOW_WIDTH), f"Width ({width}) must not be equivalent to 0!"
            assert height not in (0, -UIConfig.WINDOW_HEIGHT), f"Height ({height}) must not be equivalent to 0!"
            assert abs(width) <= UIConfig.WINDOW_WIDTH, f"Width ({width}) is out of bounds!"
            assert abs(height) <= UIConfig.WINDOW_HEIGHT, f"Height ({height}) is out of bounds!"

            # negative values are interpreted as relative to max dimensions
            if width < 0: width = UIConfig.WINDOW_WIDTH + width
            if height < 0: height = UIConfig.WINDOW_HEIGHT + height

            if margin_left is None: margin_left = 0
            if margin_top is None: margin_top = 0

            # negative margins are interpreted as absolute values from right instead of left or bottom instead of top
            if margin_left < 0: margin_left = UIConfig.WINDOW_WIDTH + margin_left
            if margin_top < 0: margin_top = UIConfig.WINDOW_HEIGHT + margin_top

            assert width + margin_left <= UIConfig.WINDOW_WIDTH, f"Invalid width or margin_left: {width} + " \
                                                                 f"{margin_left} <= {UIConfig.WINDOW_WIDTH} is False!"
            assert height + margin_top <= UIConfig.WINDOW_HEIGHT, f"Invalid height or margin_top: {height} + " \
                                                                  f"{margin_top} <= {UIConfig.WINDOW_HEIGHT} is False!"

            # default values used from WidgetSet.add_block_label()
            if pad_x is None: pad_x = 1
            if pad_y is None: pad_y = 0

            self.__width = width
            self.__height = height
            self.__margin_left = margin_left
            self.__margin_top = margin_top
            self.__pad_x = pad_x
            self.__pad_y = pad_y

        @property
        def width(self) -> int:
            return self.__width

        @property
        def height(self) -> int:
            return self.__height

        @property
        def margin_left(self) -> int:
            return self.__margin_left

        @property
        def margin_top(self) -> int:
            return self.__margin_top

        @property
        def pad_x(self) -> int:
            return self.__pad_x

        @property
        def pad_y(self) -> int:
            return self.__pad_y

        # implied properties
        @property
        def left(self) -> int:
            return self.__margin_left

        @property
        def top(self) -> int:
            return self.__margin_top

        @property
        def right(self) -> int:
            return self.__margin_left + self.__width

        @property
        def bottom(self) -> int:
            return self.__margin_top + self.__height

        def center(self, horizontal: bool = False, vertical: bool = False) -> "UIConfig.Dimensions":
            width, height, margin_left, margin_top, pad_x, pad_y = self
            if horizontal:
                margin_left = int((UIConfig.WINDOW_WIDTH - width) / 2)
            if vertical:
                margin_top = int((UIConfig.WINDOW_HEIGHT - height) / 2)
            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def align_horizontal(self, left: bool) -> "UIConfig.Dimensions":
            width, height, _, margin_top, pad_x, pad_y = self
            margin_left = 0 if left else UIConfig.WINDOW_WIDTH - width
            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def align_vertical(self, top: bool) -> "UIConfig.Dimensions":
            width, height, margin_left, _, pad_x, pad_y = self
            margin_top = 0 if top else UIConfig.WINDOW_HEIGHT - height
            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def from_base(self, new_values: Dict[str, int]):
            width, height, margin_left, margin_top, pad_x, pad_y = self
            if 'width' in new_values: width = new_values['width']
            if 'height' in new_values: height = new_values['height']

            # allow aliases for margins
            if 'margin_left' in new_values: margin_left = new_values['margin_left']
            if 'margin_x' in new_values: margin_left = new_values['margin_x']
            if 'margin_top' in new_values: margin_top = new_values['margin_top']
            if 'margin_y' in new_values: margin_top = new_values['margin_y']

            if 'pad_x' in new_values: pad_x = new_values['pad_x']
            if 'pad_y' in new_values: pad_y = new_values['pad_y']
            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def relative(self, add_values: Dict[str, int]):
            width, height, margin_left, margin_top, pad_x, pad_y = self
            if 'width' in add_values: width += add_values['width']
            if 'height' in add_values: height += add_values['height']

            # allow aliases for margins
            if 'margin_left' in add_values: margin_left += add_values['margin_left']
            if 'margin_x' in add_values: margin_left += add_values['margin_x']
            if 'margin_top' in add_values: margin_top += add_values['margin_top']
            if 'margin_y' in add_values: margin_top += add_values['margin_y']

            if 'pad_x' in add_values: pad_x += add_values['pad_x']
            if 'pad_y' in add_values: pad_y += add_values['pad_y']
            return UIConfig.Dimensions(width, height, margin_left, margin_top, pad_x, pad_y)

        def __iter__(self):
            return iter(
                (self.__width, self.__height, self.__margin_left, self.__margin_top, self.__pad_x, self.__pad_y)
            )

        def __str__(self):
            return f"WS-Dims(size={self.__width}x{self.__height}|margin={self.__margin_left},{self.__margin_top}|" \
                   f"pad:{self.__pad_x},{self.__pad_y})"

    # measures are in PyCUI rows and columns, not characters!
    WINDOW_WIDTH = 17
    WINDOW_HEIGHT = 10
    WINDOW_DIMS: Optional[Dimensions] = None

    HUD_HEIGHT = 1
    HUD_WIDTH = math.floor(WINDOW_WIDTH / 2)
    NON_HUD_HEIGHT = WINDOW_HEIGHT - HUD_HEIGHT

    PAUSE_CHOICES_WIDTH = math.floor(WINDOW_WIDTH / 3)
    PAUSE_DESCRIPTION_HEIGHT = math.floor((WINDOW_HEIGHT - HUD_HEIGHT) / 3)

    MAIN_MENU_ROW = 2
    MAIN_MENU_HEIGHT = round(WINDOW_HEIGHT / 2)
    ASCII_ART_WIDTH = math.floor(2 * WINDOW_WIDTH / 3)

    TRANSITION_SCREEN_HEIGHT = 3
    TRANSITION_SCREEN_WIDTH = 5
    TRANSITION_SCREEN_ROW = 3
    TRANSITION_SCREEN_COL = int((WINDOW_WIDTH - TRANSITION_SCREEN_WIDTH) / 2)

    INPUT_STV_WIDTH = 2
    OUTPUT_STV_WIDTH = 2
    TARGET_STV_WIDTH = 3
    STV_HEIGHT = math.floor(WINDOW_HEIGHT * 0.6)
    DIALOG_HEIGHT = 2

    LEVEL_SELECT_MAIN_X = 1
    LEVEL_SELECT_MAIN_Y = 4
    LEVEL_SELECT_MAIN_HEIGHT = 5
    LEVEL_SELECT_CHOICES_WIDTH = 3
    LEVEL_SELECT_DETAILS_WIDTH = 7

    WB_MARGIN_X = 1
    WB_ACTIONS_WIDTH = 2
    WB_INFO_HEIGHT = 2

    WB_RESOURCES_DIMS: Optional[Dimensions] = None
    WB_ACTIONS_DIMS: Optional[Dimensions] = None
    WB_GATES_DIMS: Optional[Dimensions] = None
    WB_INFOS_DIMS: Optional[Dimensions] = None

    @staticmethod
    def init():
        UIConfig.WINDOW_DIMS = UIConfig.Dimensions(width=UIConfig.WINDOW_WIDTH, height=UIConfig.WINDOW_HEIGHT)
        UIConfig._init_workbench()

    @staticmethod
    def _init_workbench():
        # first store the dimensions in local variables for better readability
        global_margin_x = 1
        res = UIConfig.Dimensions(-2*global_margin_x, 2).center(horizontal=True).align_vertical(top=True)
        infos = UIConfig.Dimensions(-2*global_margin_x, 2).center(horizontal=True).align_vertical(top=False)

        # fill actions and gates height-wise in between res and infos
        actions = UIConfig.Dimensions(3, -(res.height + infos.height), global_margin_x, res.bottom)
        gates = UIConfig.Dimensions(-(actions.right + global_margin_x), actions.height, actions.right,
                                    actions.margin_top)

        # now set the values of the global variables
        UIConfig.WB_RESOURCES_DIMS = res
        UIConfig.WB_ACTIONS_DIMS = actions
        UIConfig.WB_GATES_DIMS = gates
        UIConfig.WB_INFOS_DIMS = infos

    @staticmethod
    def wb_info_dims() -> Dimensions:
        return UIConfig.Dimensions(-2, 2).center(horizontal=True).align_vertical(top=False)
        #return UIConfig.Dimensions(UIConfig.WINDOW_WIDTH-2, 2, 1, -2)
        #return UIConfig.Dimensions.from_margins(1, -2)

    @staticmethod
    def stv_height(num_of_qubits: int) -> int:
        if num_of_qubits == 1:
            return 1
        elif num_of_qubits == 2:
            return 2
        elif num_of_qubits == 3:
            return 4
        else:
            return 6


class HudConfig:
    ShowScore = True
    ShowMapName = True
    ShowEnergy = False
    ShowKeys = True
    ShowFPS = False


# located here and not in util_functions.py because it depends on visual configs
def split_text(text: str, width: int, padding: int, handle_error: Callable[[str], None]) -> List[str]:
    """

    :param text: text to split into multiple lines
    :param width: the maximum width of one line
    :param padding: how much spaces we should place at the start and end of each line
    :param handle_error: to handle potential errors
    :return: list of text parts with a maximum of #width characters, every text part is rstrip()-ed     # todo: test thoroughly
    """
    width -= padding * 2  # remove the space needed for padding
    lines = []
    for paragraph in text.splitlines():
        paragraph = paragraph.rstrip()  # remove any redundant whitespace after the paragraph
        index = 0
        prepend: Optional[str] = None
        while True:  # technically: while index < len(paragraph), but we can only exit the loop with our break
            cur_part = paragraph[index:]

            # the beginning of a paragraph can have intentional whitespace for indentation, created lines are stripped
            if index > 0 and cur_part.startswith(" "):
                temp = cur_part.lstrip()
                # since we removed whitespace, we need to advance index so cur_part == paragraph[index:] is True again
                index += len(cur_part) - len(temp)  # the length difference tells us how many characters we removed
                cur_part = temp

            # check if the previous line ended with a color rule and prepend it
            if prepend is not None:
                cur_part = prepend + cur_part
                # we have to adapt the index since we potentially remove whitespace in front and therefore have
                # the possibility of a longer line which leads to a higher increment of the index and furthermore
                # to the potential loss of some characters in the beginning of the new_line
                # prepend also needs to be part of this adaption because it will be counted in character_removals
                index -= len(prepend)
                prepend = None

            # the currently usable width is the displayable width + the number of occurring non-printable characters
            cur_width = width + ColorConfig.count_meta_characters(cur_part, width, handle_error)

            # if cur_part fits we can skip the next steps and just append it as new line (after while, in for)
            if len(cur_part) <= cur_width:
                last_line = cur_part
                break

            # Split the line at its last reachable whitespace.
            # +1 because if the last whitespace is exactly after cur_width characters, the line still fits and the
            # additional character we get in the slice will be stripped anyways (because it's the found whitespace).
            # Since cur_part is stripped, we could start at 1, but don't due it for readability-reasons.
            last_whitespace = cur_part.rfind(" ", 0, cur_width + 1)
            if last_whitespace >= 0: cur_width = last_whitespace + 1

            next_line = cur_part[:cur_width].rstrip()
            if len(next_line) > 0:
                # check if next_line ends with an un-terminated color rule
                last_highlight = next_line.rfind(ColorConfig.TEXT_HIGHLIGHT)
                if 0 <= last_highlight < len(next_line) - ColorConfig.HIGHLIGHT_WIDTH:
                    # if so, terminate it and remember to continue it in the next line
                    code_start = last_highlight + ColorConfig.HIGHLIGHT_WIDTH
                    # TODO a highlighted number can potentially lead to problems here! (at least theoretically,
                    # todo but somehow I couldn't produce a breaking example so I might be wrong)
                    # todo also if we place an at-least-2-digits number directly after a highlight
                    if ColorConfig.is_number(next_line[code_start:code_start + ColorConfig.CODE_WIDTH]):
                        next_line += ColorConfig.TEXT_HIGHLIGHT
                        prepend = next_line[last_highlight:code_start + ColorConfig.CODE_WIDTH]
                lines.append(next_line)
            index += cur_width  # index will never increase to >= len(paragraph)

        # we don't have anything to prepend since we already added it before breaking the loop
        lines.append(last_line)

    return [" " * padding + line + " " * padding for line in lines]
