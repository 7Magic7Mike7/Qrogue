import enum
import math
from typing import Optional, Tuple

from qrogue.util.config import PyCuiColors


class ColorCode(enum.Enum):
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    ACTION_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
    WORD_HIGHLIGHT = "05"
    SPACESHIP_FLOOR = "70"

    WRONG_AMPLITUDE = "90"
    CORRECT_AMPLITUDE = "91"

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
    CORRECT_AMPLITUDE_COLOR = PyCuiColors.GREEN_ON_BLACK
    WRONG_AMPLITUDE_COLOR = PyCuiColors.RED_ON_BLACK
    CIRCUIT_COLOR = PyCuiColors.MAGENTA_ON_BLACK
    CIRCUIT_LABEL_COLOR = PyCuiColors.CYAN_ON_BLACK
    SPACESHIP_FLOOR_COLOR = PyCuiColors.BLACK_ON_WHITE
    QUESTION_SELECTION_COLOR = PyCuiColors.WHITE_ON_BLACK

    ERROR_COLOR = PyCuiColors.RED_ON_BLUE
    TEXT_HIGHLIGHT = "//"
    REGEX_TEXT_HIGHLIGHT = "//"     # regex recognizable version of TEXT_HIGHLIGHT (some characters need escaping)
    HIGHLIGHT_WIDTH = len(TEXT_HIGHLIGHT)
    __DIC = {
        str(ColorCode.TILE_HIGHLIGHT):      PyCuiColors.WHITE_ON_BLACK,
        str(ColorCode.OBJECT_HIGHLIGHT):    PyCuiColors.GREEN_ON_WHITE,
        str(ColorCode.ACTION_HIGHLIGHT):    PyCuiColors.RED_ON_WHITE,
        str(ColorCode.KEY_HIGHLIGHT):       PyCuiColors.MAGENTA_ON_WHITE,
        str(ColorCode.WORD_HIGHLIGHT):      PyCuiColors.BLUE_ON_WHITE,

        str(ColorCode.WRONG_AMPLITUDE):     PyCuiColors.RED_ON_BLACK,
        str(ColorCode.CORRECT_AMPLITUDE):   PyCuiColors.GREEN_ON_BLACK,
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
    def count_meta_characters(paragraph: str, width: int, logger) -> int:
        """
        Counts how many meta characters (i.e. not printed characters) there are in the first #width characters of
        paragraph. This way we know for example by how much we can extend the rendered text since these characters
        won't be rendered.

        :param paragraph: the str we won't to count the number of meta characters for
        :param width: number of characters we consider in paragraph (i.e. line width)
        :param logger: logs potential errors
        :return: number of found meta characters
        """
        character_removals = 0
        # check how many meta-characters (indicating color rules) we have in our line
        highlight_index = ColorConfig.__find(paragraph, 0, width)
        start = True    # whether we search for the start of a highlighted section or an end
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
                    logger.error(f"Illegal start index = {highlight_index} for \"{paragraph}\". Make sure no text"
                                 f" contains \"{ColorConfig.TEXT_HIGHLIGHT}\" or a 2 or more digit number directly"
                                 f" after a highlighting (space in-between is okay)!", from_pycui=False)
            else:
                character_removals += ColorConfig.HIGHLIGHT_WIDTH
                start = True
            highlight_index = ColorConfig.__find(paragraph, highlight_index, width + character_removals)
        return character_removals

    @staticmethod
    def colorize(color_code: ColorCode, text) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{color_code}{text}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_tile(tile: str) -> str:
        """
        Highlights tile strings.
        :param tile:
        :return:
        """
        return ColorConfig.colorize(ColorCode.TILE_HIGHLIGHT, tile)

    @staticmethod
    def highlight_object(obj: str) -> str:
        """
        Highlights something directly gameplay related. I.e. things you encounter in the game.
        :param obj:
        :return:
        """
        return ColorConfig.colorize(ColorCode.OBJECT_HIGHLIGHT, obj)

    @staticmethod
    def highlight_action(action: str) -> str:
        """
        Highlights action words that explain what you can do in the game.
        :param action:
        :return:
        """
        return ColorConfig.colorize(ColorCode.ACTION_HIGHLIGHT, action)

    @staticmethod
    def highlight_key(key: str) -> str:
        """
        Highlights a keyboard input.
        :param key:
        :return:
        """
        return ColorConfig.colorize(ColorCode.KEY_HIGHLIGHT, key)

    @staticmethod
    def highlight_word(word: str) -> str:
        """
        Highlights miscellaneous words that should be highlighted.
        :param word:
        :return:
        """
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
    __DEFAULT_POS = 0
    __TOP_POS = 3
    __RIGHT_POS = 111
    __BOT_POS = 22
    __LEFT_POS = 3
    __POSITIONS = [
        None, (None, __TOP_POS), (__RIGHT_POS, __TOP_POS), (__RIGHT_POS, None), (__RIGHT_POS, __BOT_POS),
        (None, __BOT_POS), (__LEFT_POS, __BOT_POS), (__LEFT_POS, None), (__LEFT_POS, __TOP_POS)
    ]

    PADDING_X = 2
    PADDING_Y = 2

    @staticmethod
    def default_color() -> int:
        return PyCuiColors.BLACK_ON_WHITE

    @staticmethod
    def default_pos() -> int:
        assert 0 <= PopupConfig.__DEFAULT_POS < len(PopupConfig.__POSITIONS)
        return PopupConfig.__DEFAULT_POS

    @staticmethod
    def resolve_position(position: int) -> Optional[Tuple[Optional[int], Optional[int]]]:
        if 0 <= position < len(PopupConfig.__POSITIONS):
            return PopupConfig.__POSITIONS[position]
        else:
            return PopupConfig.resolve_position(PopupConfig.default_pos())

    # sizes don't work as easy as positions somehow


class UIConfig:
    WINDOW_WIDTH = 17
    WINDOW_HEIGHT = 10

    HUD_HEIGHT = 1
    HUD_WIDTH = math.floor(WINDOW_WIDTH / 2)
    NON_HUD_HEIGHT = WINDOW_HEIGHT - HUD_HEIGHT

    PAUSE_CHOICES_WIDTH = math.floor(WINDOW_WIDTH / 3)
    PAUSE_DESCRIPTION_HEIGHT = math.floor((WINDOW_HEIGHT - HUD_HEIGHT) / 3)

    MAIN_MENU_ROW = 2
    MAIN_MENU_HEIGHT = round(WINDOW_HEIGHT / 2)
    ASCII_ART_WIDTH = math.floor(2 * WINDOW_WIDTH / 3)

    TRANSITION_SCREEN_ROW = 3
    TRANSITION_SCREEN_COL = 0
    TRANSITION_SCREEN_HEIGHT = 4
    TRANSITION_SCREEN_WIDTH = WINDOW_WIDTH

    INPUT_STV_WIDTH = 2
    OUTPUT_STV_WIDTH = 2
    TARGET_STV_WIDTH = 3
    STV_HEIGHT = math.floor(WINDOW_HEIGHT * 0.6)
    DIALOG_HEIGHT = 2
    PUZZLE_CHOICES_WIDTH = math.floor(WINDOW_WIDTH / 3)

    SHOP_INVENTORY_WIDTH = 4
    SHOP_DETAILS_HEIGHT = 1

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
    ShowMapName = False
    ShowEnergy = False
    ShowKeys = False
    ShowCoins = False
    ShowFPS = False
