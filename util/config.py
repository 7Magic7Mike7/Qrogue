import os
from datetime import datetime

import py_cui


class PathConfig:
    __BASE_PATH = ".."
    __LOG_FOLDER = "logs"
    __KEY_LOG_FOLDER = "keylogs"
    __SCREEN_PRINTS_FOLDER = "screenprints"

    @staticmethod
    def create_data_folder(base_path: str) -> None:
        log_path = os.path.join(base_path, PathConfig.__LOG_FOLDER)
        key_log_path = os.path.join(base_path, PathConfig.__KEY_LOG_FOLDER)
        screen_prints_path = os.path.join(base_path, PathConfig.__SCREEN_PRINTS_FOLDER)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(key_log_path):
            os.mkdir(key_log_path)
        if not os.path.exists(screen_prints_path):
            os.mkdir(screen_prints_path)

    @staticmethod
    def set_base_path() -> bool:
        config_file_path = os.path.join(os.path.dirname(__file__), "..", "installer", "qrogue.config")
        try:
            with open(config_file_path) as f:
                content = f.readlines()
                # ignore the last character because it is \n
                PathConfig.__BASE_PATH = content[1][:-1]
            return os.path.exists(PathConfig.__BASE_PATH)
        except:
            return False

    @staticmethod
    def base_path(file_name: str = "") -> str:
        return os.path.join(PathConfig.__BASE_PATH, file_name)

    @staticmethod
    def new_log_file(seed: int) -> str:
        now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        return os.path.join(PathConfig.__LOG_FOLDER, f"{now_str}_seed{seed}.qrlog")

    @staticmethod
    def new_key_log_file() -> str:
        now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}.qrkl")

    @staticmethod
    def new_screen_print(text: str):
        now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name = os.path.join(PathConfig.__SCREEN_PRINTS_FOLDER, f"{now_str}.qrsc")
        PathConfig.write(file_name, now_str + "\n" + text, True, True)

    @staticmethod
    def write(file_name: str, text: str, may_exist: bool = True, append: bool = False):
        path = PathConfig.base_path(file_name)
        mode = "x"
        if may_exist:
            if os.path.exists(path):
                mode = "w"
                if append:
                    mode = "a"
        with open(path, mode) as file:
            file.write(text)

    @staticmethod
    def read_keylog_buffered(file_name: str, in_keylog_folder: bool = True, buffer_size: int = 1024) -> str:
        if in_keylog_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__KEY_LOG_FOLDER, file_name))
        else:
            path = file_name
        if os.path.exists(path):
            with open(path, "r") as file:
                data = file.read(buffer_size)
                while data:
                    yield data
                    data = file.read(buffer_size)
        return None

    @staticmethod
    def read(file_name: str, in_base_path: bool = True) -> str:
        if in_base_path:
            path = PathConfig.base_path(file_name)
        else:
            path = file_name
        content = ""
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
        return content

    @staticmethod
    def delete(file_name):
        path = PathConfig.base_path(file_name)
        if os.path.exists(path):
            os.remove(path)


class MapConfig:
    @staticmethod
    def tutorial_seed() -> int:
        return 0


class ColorConfig:
    SELECTION_HIGHLIGHT = py_cui.BLACK_ON_WHITE
    QUBIT_INFO_COLOR = py_cui.CYAN_ON_BLACK
    STV_HEADING_COLOR = py_cui.CYAN_ON_BLACK
    CORRECT_AMPLITUDE_COLOR = py_cui.GREEN_ON_BLACK
    CIRCUIT_COLOR = py_cui.CYAN_ON_BLACK

    ERROR_COLOR = py_cui.RED_ON_BLUE
    TEXT_HIGHLIGHT = "//"
    REGEX_TEXT_HIGHLIGHT = "//"
    HIGHLIGHT_WIDTH = len(TEXT_HIGHLIGHT)
    CODE_WIDTH = 2
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    WORD_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
    __DIC = {
        TILE_HIGHLIGHT: py_cui.WHITE_ON_BLACK,
        OBJECT_HIGHLIGHT: py_cui.BLUE_ON_WHITE,
        WORD_HIGHLIGHT: py_cui.RED_ON_WHITE,
        KEY_HIGHLIGHT: py_cui.MAGENTA_ON_WHITE,
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
                    elif ColorConfig.is_punctuation(paragraph[-1]): # TODO I don't think -1 is correct, because it is
                                                                    # todo the very end, but somehow it works
                        # if the very last word is highlighted we also have no whitespace at the end
                        character_removals += ColorConfig.HIGHLIGHT_WIDTH + ColorConfig.CODE_WIDTH \
                                              + ColorConfig.HIGHLIGHT_WIDTH
                        break
                    else:
                        break
                else:
                    logger.error(f"Illegal start index = {highlight_index} for \"{paragraph}\". Make sure no text"
                                 f" contains \"{ColorConfig.TEXT_HIGHLIGHT}\" or a 2 or more digit number directly"
                                 f" after a highlighting (space in-between is okay)!")
            else:
                character_removals += ColorConfig.HIGHLIGHT_WIDTH
                start = True
            highlight_index = ColorConfig.__find(paragraph, highlight_index, width + character_removals)
        return character_removals

    @staticmethod
    def __highlight(type: str, text) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{type}{text}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_tile(tile: str) -> str:
        """
        Highlights tile strings.
        :param tile:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.TILE_HIGHLIGHT, tile)

    @staticmethod
    def highlight_object(obj: str) -> str:
        """
        Highlights something directly gameplay related. I.e. things you encounter in the game.
        :param obj:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.OBJECT_HIGHLIGHT, obj)

    @staticmethod
    def highlight_word(word: str) -> str:
        """
        Highlights special words that explain gameplay but are not encountered in the game themselves.
        :param word:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.WORD_HIGHLIGHT, word)

    @staticmethod
    def highlight_key(key: str) -> str:
        """
        Highlights a keyboard input.
        :param key:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.KEY_HIGHLIGHT, key)

    @staticmethod
    def get(char: str):
        try:
            return ColorConfig.__DIC[char]
        except KeyError:
            return ColorConfig.ERROR_COLOR


class PopupConfig:
    @staticmethod
    def default_color() -> int:
        return py_cui.BLACK_ON_WHITE


class CheatConfig:
    INPUT_CHEAT_KEY = py_cui.keys.KEY_CTRL_I
    CHEAT_LIST_KEY = py_cui.keys.KEY_CTRL_L
    __ALL = "aLL"
    __GOD_MODE = "Qod-Mode"
    __SCARED_RABBIT = "Rabbit_Tunnel"
    __INF_RESOURCES = "Rich"
    __NONE = "n0n3"
    __CHEATS = {
        __GOD_MODE: False,
        __SCARED_RABBIT: False,
        __INF_RESOURCES: False,
    }
    __cheated = False
    __popup = None
    __input_popup = None

    @staticmethod
    def init(popup_callback: "(str, str, int)", input_popup_callback: "(str, int, (str,))"):
        CheatConfig.__cheated = False
        CheatConfig.__popup = popup_callback
        CheatConfig.__input_popup = input_popup_callback
        for key in CheatConfig.__CHEATS:
            CheatConfig.__CHEATS[key] = False

    @staticmethod
    def did_cheat() -> bool:
        return CheatConfig.__cheated

    @staticmethod
    def in_god_mode() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__GOD_MODE]

    @staticmethod
    def is_scared_rabbit() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__SCARED_RABBIT]

    @staticmethod
    def got_inf_resources() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__INF_RESOURCES]

    @staticmethod
    def cheat_input():
        if CheatConfig.__input_popup is not None:
            CheatConfig.__input_popup("Input your Cheat:", py_cui.BLACK_ON_RED, CheatConfig.__use_cheat)

    @staticmethod
    def cheat_list():
        text = ""
        for key in CheatConfig.__CHEATS:
            text += f"{key}: \t\t"
            if CheatConfig.__CHEATS[key]:
                text += "Active\n"
            else:
                text += "Inactive\n"
        CheatConfig.__popup("List of Cheats", text, PopupConfig.default_color())

    @staticmethod
    def __use_cheat(code: str) -> bool:
        ret = False
        if code == CheatConfig.__ALL or code == CheatConfig.__NONE:
            for key in CheatConfig.__CHEATS:
                CheatConfig.__CHEATS[key] = code == CheatConfig.__ALL
            ret = True
        elif code in CheatConfig.__CHEATS:
            CheatConfig.__CHEATS[code] = not CheatConfig.__CHEATS[code]
            ret = True

        if ret:
            CheatConfig.__popup("Cheats", f"Successfully used the Cheat \"{code}\"", PopupConfig.default_color())
            CheatConfig.__cheated = True
        else:
            CheatConfig.__popup("Cheats", "This is not a valid Cheat!")
        return ret


class GameplayConfig:
    __KEY_VALUE_SEPARATOR = "="

    __AUTO_RESET_CIRCUIT = "Auto reset Circuit"
    __LOG_KEYS = "Log Keys"
    __SIMULATION_KEY_PAUSE = "Simulation key pause"
    __GAMEPLAY_KEY_PAUSE = "Gameplay key pause"
    __CONFIG = {
        __AUTO_RESET_CIRCUIT: ("True", "Automatically reset your Circuit to a clean state at the beginning of a Fight, "
                                     "Riddle, etc."),
        __LOG_KEYS: ("True", "Stores all keys you pressed in a .qrkl-file so one can replay them (e.g. for analysing a "
                           "bug)"),
        __SIMULATION_KEY_PAUSE: ("0.2", "How long to wait before we process the next input during simulation."),
        __GAMEPLAY_KEY_PAUSE: ("0.2", "How long to wait before we process the next input during gameplay."),
    }

    @staticmethod
    def to_file_text() -> str:
        text = ""
        for conf in GameplayConfig.__CONFIG:
            text += f"{conf}{GameplayConfig.__KEY_VALUE_SEPARATOR}{GameplayConfig.__CONFIG[conf][0]}"
            text += "\n"
        return text

    @staticmethod
    def from_log_text(log_text: str) -> bool:
        for line in log_text.splitlines():
            split = line.split(GameplayConfig.__KEY_VALUE_SEPARATOR)
            try:
                GameplayConfig.__CONFIG[split[0]] = [split[1]]
            except IndexError:
                return False
            except KeyError:
                return False
        return True

    @staticmethod
    def auto_reset_circuit() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_RESET_CIRCUIT][0] == "True"

    @staticmethod
    def log_keys() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__LOG_KEYS][0] == "True"

    @staticmethod
    def simulation_key_pause() -> float:
        try:
            return float(GameplayConfig.__CONFIG[GameplayConfig.__SIMULATION_KEY_PAUSE][0])
        except:
            return 0.2

    @staticmethod
    def gameplay_key_pause() -> float:
        try:
            return float(GameplayConfig.__CONFIG[GameplayConfig.__GAMEPLAY_KEY_PAUSE][0])
        except:
            return 0.4


class Config:
    __VERSION = "v0.0.1"
    __GAME_CONFIG = "qrogue_game.config"
    __GAMEPLAY_HEAD = "[Gameplay]\n"

    @staticmethod
    def version() -> str:
        return Config.__VERSION

    @staticmethod
    def create():
        text = ""
        text += Config.__GAMEPLAY_HEAD
        text += GameplayConfig.to_file_text()

        file_path = os.path.join(os.path.dirname(__file__), "..", "installer", "qrogue.config")
        config_content = PathConfig.read(file_path, False).splitlines()
        PathConfig.create_data_folder(config_content[1])
        path = os.path.join(config_content[1], Config.__GAME_CONFIG)
        with open(path, "x") as file:
            file.write(text)

    @staticmethod
    def load():
        if not PathConfig.set_base_path():
            return 1

        if not os.path.exists(os.path.join(PathConfig.base_path(), Config.__GAME_CONFIG)):
            Config.create()

        config = PathConfig.read(Config.__GAME_CONFIG)

        gameplay_section = config.index(Config.__GAMEPLAY_HEAD) + len(Config.__GAMEPLAY_HEAD)
        gameplay_section = (gameplay_section, len(config))
        if not GameplayConfig.from_log_text(config[gameplay_section[0]:gameplay_section[1]]):
            return 2

        return 0
