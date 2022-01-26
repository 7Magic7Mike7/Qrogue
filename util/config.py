import enum
import os
from datetime import datetime

import py_cui


class FileTypes(enum.Enum):
    Log = ".qrlog"
    KeyLog = ".qrkl"
    ScreenPrint = ".qrsc"
    Save = ".qrsave"
    Dungeon = ".qrdg"
    Templates = ".txt"


class PathConfig:
    __BASE_PATH = ".."
    __LOG_FOLDER = "logs"
    __KEY_LOG_FOLDER = "keylogs"
    __SCREEN_PRINTS_FOLDER = "screenprints"
    __SAVE_DATA_FOLDER = "saves"
    __DUNGEON_FOLDER = os.path.join("data", "dungeons")
    __TEMPLATE_ROOMS = os.path.join("data", "rooms")
    __TEMPLATE_HALLWAYS = os.path.join("data", "hallways")
    __TEMPLATE_STV_POOLS = os.path.join("data", "stv_pools")
    __TEMPLATE_REWARD_POOLS = os.path.join("data", "reward_pools")
    __TEMPLATE_FILE = f"templates{FileTypes.Templates}"

    __SAVE_FILE_NUMERATION_SEPARATOR = "_"

    @staticmethod
    def __now_str() -> str:
        return datetime.now().strftime("%d%m%Y_%H%M%S")

    @staticmethod
    def create_data_folder(base_path: str) -> None:
        log_path = os.path.join(base_path, PathConfig.__LOG_FOLDER)
        key_log_path = os.path.join(base_path, PathConfig.__KEY_LOG_FOLDER)
        screen_prints_path = os.path.join(base_path, PathConfig.__SCREEN_PRINTS_FOLDER)
        save_data_path = os.path.join(base_path, PathConfig.__SAVE_DATA_FOLDER)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(key_log_path):
            os.mkdir(key_log_path)
        if not os.path.exists(screen_prints_path):
            os.mkdir(screen_prints_path)
        if not os.path.exists(save_data_path):
            os.mkdir(save_data_path)

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
        now_str = PathConfig.__now_str()
        return os.path.join(PathConfig.__LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.Log.value}")

    @staticmethod
    def new_key_log_file(seed) -> (str, str):
        now_str = PathConfig.__now_str()
        return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.KeyLog.value}")

    @staticmethod
    def new_screen_print(text: str):
        now_str = PathConfig.__now_str()
        file_name = os.path.join(PathConfig.__SCREEN_PRINTS_FOLDER, f"{now_str}{FileTypes.ScreenPrint.value}")
        PathConfig.write(file_name, now_str + "\n" + text, True, True)

    @staticmethod
    def new_save_file(text: str):
        now_str = PathConfig.__now_str()
        num = 0
        # todo list files of folder to find out the next number and if we delete a previous save
        file_name = os.path.join(PathConfig.__SAVE_DATA_FOLDER,
                                 f"qrogue-save{PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR}{num}{FileTypes.Save.value}")
        PathConfig.write(file_name, now_str + "\n" + text, False, False)

    @staticmethod
    def find_latest_save_file() -> str:
        folder = os.path.join(PathConfig.__BASE_PATH, PathConfig.__SAVE_DATA_FOLDER)
        files = os.listdir(folder)
        num = 0
        for file in files:
            file_ending_index = file.rindex(FileTypes.Save.value)
            cur_num = int(file[file.rindex(PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR) + 1:file_ending_index])
            if cur_num > num:
                num = cur_num
        return f"qrogue-save{PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR}{num}{FileTypes.Save.value}"

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
        if not file_name.endswith(FileTypes.KeyLog.value):
            file_name += FileTypes.KeyLog.value
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
        else:
            raise FileNotFoundError(f"There is no such key log file: {path}")

    @staticmethod
    def read_dungeon(file_name: str, in_dungeon_folder: bool = True):
        if not file_name.endswith(FileTypes.Dungeon.value):
            file_name += FileTypes.Dungeon.value

        if in_dungeon_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__DUNGEON_FOLDER, file_name))
        else:
            path = file_name
        return PathConfig.read(path, in_base_path=False)

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
        else:
            raise FileNotFoundError(f"File \"{file_name}\" could not be found!")
        return content

    @staticmethod
    def delete(file_name):
        path = PathConfig.base_path(file_name)
        if os.path.exists(path):
            os.remove(path)


class ColorCode(enum.Enum):
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    WORD_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
    SPACESHIP_FLOOR = "70"

    def __init__(self, code: str):
        self.__code = code

    def __str__(self):
        return self.__code


class ColorConfig:
    CODE_WIDTH = 2
    SELECTION_COLOR = py_cui.BLACK_ON_WHITE
    QUBIT_INFO_COLOR = py_cui.CYAN_ON_BLACK
    STV_HEADING_COLOR = py_cui.CYAN_ON_BLACK
    CORRECT_AMPLITUDE_COLOR = py_cui.GREEN_ON_BLACK
    WRONG_AMPLITUDE_COLOR = py_cui.RED_ON_BLACK
    CIRCUIT_COLOR = py_cui.CYAN_ON_BLACK

    ERROR_COLOR = py_cui.RED_ON_BLUE
    TEXT_HIGHLIGHT = "//"
    REGEX_TEXT_HIGHLIGHT = "//"     # regex recognizable version of TEXT_HIGHLIGHT (some characters need escaping)
    HIGHLIGHT_WIDTH = len(TEXT_HIGHLIGHT)
    __DIC = {
        str(ColorCode.TILE_HIGHLIGHT): py_cui.WHITE_ON_BLACK,
        str(ColorCode.OBJECT_HIGHLIGHT): py_cui.BLUE_ON_WHITE,
        str(ColorCode.WORD_HIGHLIGHT): py_cui.RED_ON_WHITE,
        str(ColorCode.KEY_HIGHLIGHT): py_cui.MAGENTA_ON_WHITE,

        str(ColorCode.SPACESHIP_FLOOR): py_cui.BLACK_ON_WHITE,
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
    def highlight_word(word: str) -> str:
        """
        Highlights special words that explain gameplay but are not encountered in the game themselves.
        :param word:
        :return:
        """
        return ColorConfig.colorize(ColorCode.WORD_HIGHLIGHT, word)

    @staticmethod
    def highlight_key(key: str) -> str:
        """
        Highlights a keyboard input.
        :param key:
        :return:
        """
        return ColorConfig.colorize(ColorCode.KEY_HIGHLIGHT, key)

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
    @staticmethod
    def default_color() -> int:
        return py_cui.BLACK_ON_WHITE


class CheatConfig:
    __ALL = "aLL"
    __GOD_MODE = "Qod-Mode"
    __SCARED_RABBIT = "Rabbit_Tunnel"
    __INF_RESOURCES = "Rich"
    __MAP_REVEAL = "Illuminati"
    __NONE = "n0n3"
    __CHEATS = {
        __GOD_MODE: False,
        __SCARED_RABBIT: False,
        __INF_RESOURCES: False,
        __MAP_REVEAL: False,
    }
    __cheated = False
    __popup = None
    __input_popup = None

    @staticmethod
    def init(popup_callback: "(str, str, int)", input_popup_callback: "(str, int, (str,))"):
        CheatConfig.__cheated = False
        CheatConfig.__popup = popup_callback
        CheatConfig.__input_popup = input_popup_callback
        # deactivate cheats if we are not debugging
        if not Config.debugging():
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
    def revealed_map() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__MAP_REVEAL]

    @staticmethod
    def cheat_input():
        if Config.debugging() and CheatConfig.__input_popup is not None:
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
        __GAMEPLAY_KEY_PAUSE: ("0.1", "How long to wait before we process the next input during gameplay."),
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


class Config:   # todo make singleton and handle access to other configs?
    MAX_SEED = 1000000
    __VERSION = "v0.2"
    __GAME_CONFIG = "qrogue_game.config"
    __GAMEPLAY_HEAD = "[Gameplay]\n"
    __DEBUG = False

    __HEADER = "Qrogue "
    __SEED_HEAD = "Seed="
    __TIME_HEAD = "Time="
    __CONFIG_HEAD = "[Config]"

    @staticmethod
    def version() -> str:
        return Config.__VERSION

    @staticmethod
    def get_log_head(seed: int) -> str:
        now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        head = f"{Config.__HEADER}{Config.version()}\n"
        head += f"{Config.__SEED_HEAD}{seed}\n"
        head += f"{Config.__TIME_HEAD}{now_str}\n\n"
        head += f"{Config.__CONFIG_HEAD}\n{GameplayConfig.to_file_text()}\n"
        return head

    @staticmethod
    def config_file() -> str:
        return Config.__GAME_CONFIG

    @staticmethod
    def debugging() -> bool:
        return Config.__DEBUG

    @staticmethod
    def activate_debugging():
        Config.__DEBUG = True

    @staticmethod
    def create():
        text = ""
        text += Config.__GAMEPLAY_HEAD
        text += GameplayConfig.to_file_text()

        file_path = os.path.join(os.path.dirname(__file__), "..", "installer", "qrogue.config")
        try:
            config_content = PathConfig.read(file_path, False).splitlines()
        except FileNotFoundError:
            raise FileNotFoundError("Could not find the base config file qrogue.config\nPlease download the installer "
                                    "folder again!")
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

        try:
            config = PathConfig.read(Config.__GAME_CONFIG)
        except FileNotFoundError:
            raise FileNotFoundError("Could not load the game's config file!")

        gameplay_section = config.index(Config.__GAMEPLAY_HEAD) + len(Config.__GAMEPLAY_HEAD)
        gameplay_section = (gameplay_section, len(config))
        if not GameplayConfig.from_log_text(config[gameplay_section[0]:gameplay_section[1]]):
            return 2

        return 0
