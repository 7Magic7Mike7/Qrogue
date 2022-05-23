import enum
import math
import os
import pathlib
from datetime import datetime
from typing import Callable, Tuple

from qrogue.util import PyCuiColors


class FileTypes(enum.Enum):
    Log = ".qrlog"
    KeyLog = ".qrkl"
    ScreenPrint = ".qrsc"
    Save = ".qrsave"
    Dungeon = ".qrdg"
    World = ".qrw"
    Templates = ".txt"


class PathConfig:
    __DEFAULT_GAME_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
    __DEFAULT_USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "QrogueData")
    __DATA_FOLDER = "data"
    __LOG_FOLDER = "logs"
    __KEY_LOG_FOLDER = "keylogs"
    __SCREEN_PRINTS_FOLDER = "screenprints"
    __SAVE_DATA_FOLDER = "saves"
    __DUNGEON_FOLDER = "dungeons"
    __TEMPLATE_ROOMS = "rooms"
    __TEMPLATE_HALLWAYS = "hallways"
    __TEMPLATE_STV_POOLS = "stv_pools"
    __TEMPLATE_REWARD_POOLS = "reward_pools"
    __TEMPLATE_FILE = f"templates{FileTypes.Templates.value}"
    __FRESH_SAVE_FILE = "fresh"
    __SAVE_FILE_NUMERATION_SEPARATOR = "_"
    __NUMBER_OF_SAVE_FILES = 7    # how many save files can be present before we delete the oldest one

    __Base_Path = __DEFAULT_GAME_DATA_PATH
    __User_Data_Path = __DEFAULT_USER_DATA_PATH

    @staticmethod
    def __now_str() -> str:
        return datetime.now().strftime("%d%m%Y_%H%M%S")

    @staticmethod
    def __save_file_str(num: int) -> str:
        return os.path.join(PathConfig.__SAVE_DATA_FOLDER,
                            f"qrogue-save{PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR}{num}{FileTypes.Save.value}")

    @staticmethod
    def __get_save_files_stats() -> Tuple[int, int]:
        """

        :return: number of available save files, number of the latest save file
        """
        files = os.listdir(PathConfig.user_data_path(PathConfig.__SAVE_DATA_FOLDER))
        num = -1
        num_of_files = 0
        for file in files:
            if file.endswith(FileTypes.Save.value):
                file_ending_index = len(file) - len(FileTypes.Save.value)
                num_of_files += 1
                cur_num = int(file[file.rindex(PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR) + 1:file_ending_index])
                if cur_num > num:
                    num = cur_num
        return num_of_files, num

    @staticmethod
    def launch_config_path() -> str:
        return os.path.join(os.path.dirname(__file__), "..", PathConfig.__DATA_FOLDER, "qrogue_launch.config")

    @staticmethod
    def default_base_path() -> str:
        return PathConfig.__DEFAULT_GAME_DATA_PATH

    @staticmethod
    def default_user_data_path() -> str:
        return PathConfig.__DEFAULT_USER_DATA_PATH

    @staticmethod
    def create_folder_structure(user_data_path: str) -> None:
        pathlib.Path(user_data_path).mkdir(parents=True, exist_ok=True)
        log_path = os.path.join(user_data_path, PathConfig.__LOG_FOLDER)
        key_log_path = os.path.join(user_data_path, PathConfig.__KEY_LOG_FOLDER)
        screen_prints_path = os.path.join(user_data_path, PathConfig.__SCREEN_PRINTS_FOLDER)
        save_data_path = os.path.join(user_data_path, PathConfig.__SAVE_DATA_FOLDER)

        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(key_log_path):
            os.mkdir(key_log_path)
        if not os.path.exists(screen_prints_path):
            os.mkdir(screen_prints_path)
        if not os.path.exists(save_data_path):
            os.mkdir(save_data_path)

    @staticmethod
    def set_base_path(base_path: str):
        if os.path.exists(base_path):
            PathConfig.__Base_Path = base_path
        else:
            raise FileNotFoundError(f"Given base path is not valid: {base_path}")

    @staticmethod
    def set_user_data_path(user_data_path: str):
        PathConfig.create_folder_structure(user_data_path)  # does nothing for existing folders
        PathConfig.__User_Data_Path = user_data_path

    @staticmethod
    def load_paths(custom_data_path: str, custom_user_data_path: str) -> bool:
        try:
            if custom_data_path is None or custom_user_data_path is None:
                with open(PathConfig.launch_config_path()) as f:
                    content = f.readlines()

            if custom_data_path:
                data_path = custom_data_path
            else:
                data_path = content[1]
            if custom_user_data_path:
                user_data_path = custom_user_data_path
            else:
                user_data_path = content[2]

            if data_path == "\n":
                data_path = PathConfig.default_base_path()
            elif data_path.endswith("\n"):
                data_path = data_path[:-1]
            if user_data_path == "\n":
                user_data_path = PathConfig.default_user_data_path()
            elif user_data_path.endswith("\n"):
                user_data_path = user_data_path[:-1]

            PathConfig.set_base_path(data_path)
            PathConfig.set_user_data_path(user_data_path)
            return os.path.exists(PathConfig.__Base_Path) and os.path.exists(PathConfig.__User_Data_Path)
        except:
            return False

    @staticmethod
    def base_path(file_name: str = "") -> str:
        return os.path.join(PathConfig.__Base_Path, file_name)

    @staticmethod
    def user_data_path(file_name: str = "") -> str:
        return os.path.join(PathConfig.__User_Data_Path, file_name)

    @staticmethod
    def new_log_file(seed: int) -> str:
        now_str = PathConfig.__now_str()
        return os.path.join(PathConfig.__LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.Log.value}")

    @staticmethod
    def new_key_log_file(seed: int, is_level: bool = True) -> str:
        now_str = PathConfig.__now_str()
        if is_level:
            return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.KeyLog.value}")
        else:
            return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}_meta{seed}{FileTypes.KeyLog.value}")

    @staticmethod
    def new_screen_print(text: str):
        now_str = PathConfig.__now_str()
        path = os.path.join(PathConfig.__SCREEN_PRINTS_FOLDER, f"{now_str}{FileTypes.ScreenPrint.value}")
        PathConfig.write(path, now_str + "\n" + text, may_exist=True, append=True)

    @staticmethod
    def new_save_file(text: str):
        now_str = PathConfig.__now_str()
        num_of_files, num = PathConfig.__get_save_files_stats()
        num += 1    # increment to get the highest number for the new save file (if no save file exists yet,
                    # -1 will be incremented to 0)
        if num_of_files >= PathConfig.__NUMBER_OF_SAVE_FILES:
            oldest_num = num - PathConfig.__NUMBER_OF_SAVE_FILES
            PathConfig.delete(PathConfig.__save_file_str(oldest_num))
        PathConfig.write(PathConfig.__save_file_str(num), now_str + "\n" + text, may_exist=False)

    @staticmethod
    def find_latest_save_file() -> str:
        _, num = PathConfig.__get_save_files_stats()
        if num >= 0:
            return PathConfig.__save_file_str(num)
        else:
            return PathConfig.base_path(f"{PathConfig.__FRESH_SAVE_FILE}{FileTypes.Save.value}")

    @staticmethod
    def read_keylog_buffered(file_name: str, in_keylog_folder: bool = True, buffer_size: int = 1024) -> str:
        if not file_name.endswith(FileTypes.KeyLog.value):
            file_name += FileTypes.KeyLog.value
        if in_keylog_folder:
            path = PathConfig.user_data_path(os.path.join(PathConfig.__KEY_LOG_FOLDER, file_name))
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
    def read_world(file_name: str, in_dungeon_folder: bool = True):
        if not file_name.endswith(FileTypes.World.value):
            file_name += FileTypes.World.value

        if in_dungeon_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__DUNGEON_FOLDER, file_name))
        else:
            path = file_name
        return PathConfig.read(path, in_user_path=False)

    @staticmethod
    def read_level(file_name: str, in_dungeon_folder: bool = True):
        if not file_name.endswith(FileTypes.Dungeon.value):
            file_name += FileTypes.Dungeon.value

        if in_dungeon_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__DUNGEON_FOLDER, file_name))
        else:
            path = file_name
        return PathConfig.read(path, in_user_path=False)

    @staticmethod
    def read(file_name: str, in_user_path: bool) -> str:
        if in_user_path:
            path = PathConfig.user_data_path(file_name)
        else:
            path = file_name
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
            return content
        else:
            raise FileNotFoundError(f"File \"{file_name}\" could not be found!")

    @staticmethod
    def write(path: str, text: str, in_user_path: bool = True, may_exist: bool = True, append: bool = False):
        if in_user_path:
            path = PathConfig.user_data_path(path)  # data in base_path is static so we can only write user data
        mode = "x"
        if may_exist:
            if os.path.exists(path):
                mode = "w"
                if append:
                    mode = "a"
        with open(path, mode) as file:
            file.write(text)

    @staticmethod
    def delete(file_name):
        path = PathConfig.user_data_path(file_name)     # data in base_path is static so we can only delete user data
        if os.path.exists(path):
            os.remove(path)


class ColorCode(enum.Enum):
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    WORD_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
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
    STV_HEADING_COLOR = PyCuiColors.CYAN_ON_BLACK
    CORRECT_AMPLITUDE_COLOR = PyCuiColors.GREEN_ON_BLACK
    WRONG_AMPLITUDE_COLOR = PyCuiColors.RED_ON_BLACK
    CIRCUIT_COLOR = PyCuiColors.MAGENTA_ON_BLACK
    CIRCUIT_LABEL_COLOR = PyCuiColors.CYAN_ON_BLACK
    SPACESHIP_FLOOR_COLOR = PyCuiColors.BLACK_ON_WHITE

    ERROR_COLOR = PyCuiColors.RED_ON_BLUE
    TEXT_HIGHLIGHT = "//"
    REGEX_TEXT_HIGHLIGHT = "//"     # regex recognizable version of TEXT_HIGHLIGHT (some characters need escaping)
    HIGHLIGHT_WIDTH = len(TEXT_HIGHLIGHT)
    __DIC = {
        str(ColorCode.TILE_HIGHLIGHT):      PyCuiColors.WHITE_ON_BLACK,
        str(ColorCode.OBJECT_HIGHLIGHT):    PyCuiColors.BLUE_ON_WHITE,
        str(ColorCode.WORD_HIGHLIGHT):      PyCuiColors.RED_ON_WHITE,
        str(ColorCode.KEY_HIGHLIGHT):       PyCuiColors.MAGENTA_ON_WHITE,
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
        return PyCuiColors.BLACK_ON_WHITE


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
    def init(popup_callback: Callable[[str, str, int], None],
             input_popup_callback: Callable[[str, int, Callable[[str], None]], None]):
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
            CheatConfig.__input_popup("Input your Cheat:", PyCuiColors.BLACK_ON_RED, CheatConfig.__use_cheat)

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
            CheatConfig.__popup("Cheats", "This is not a valid Cheat!", PopupConfig.default_color())
        return ret


class GameplayConfig:
    __KEY_VALUE_SEPARATOR = "="

    __AUTO_SAVE = "Auto save on exit"
    __AUTO_RESET_CIRCUIT = "Auto reset Circuit"
    __AUTO_SWAP_GATES = "Auto swap Gates"
    __LOG_KEYS = "Log Keys"
    __SIMULATION_KEY_PAUSE = "Simulation key pause"
    __GAMEPLAY_KEY_PAUSE = "Gameplay key pause"
    __CONFIG = {
        __AUTO_SAVE: ("True", "Automatically saves the game when you exit it."),
        __AUTO_RESET_CIRCUIT: ("True", "Automatically reset your Circuit to a clean state at the beginning of a Fight, "
                                     "Riddle, etc."),
        __AUTO_SWAP_GATES: ("True", "Automatically swaps position of two gates if you try to move one to an occupied "
                                    "slot."),
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
    def auto_save() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_SAVE][0] == "True"

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

    @staticmethod
    def auto_swap_gates() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_SWAP_GATES][0] == "True"


class UIConfig:
    WINDOW_WIDTH = 17
    WINDOW_HEIGHT = 10

    HUD_HEIGHT = 1
    NON_HUD_HEIGHT = WINDOW_HEIGHT - HUD_HEIGHT
    PAUSE_CHOICES_WIDTH = math.floor(WINDOW_WIDTH / 3)

    MAIN_MENU_ROW = 2
    MAIN_MENU_HEIGHT = round(WINDOW_HEIGHT / 2)
    ASCII_ART_WIDTH = math.floor(2 * WINDOW_WIDTH / 3)

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
    ShowMapName = True
    ShowEnergy = True
    ShowKeys = True
    ShowCoins = True
    ShowFPS = False


class MapConfig:
    @staticmethod
    def max_width() -> int:
        return 7

    @staticmethod
    def max_height() -> int:
        return 3

    @staticmethod
    def done_event_id() -> str:
        return "done"

    @staticmethod
    def specific_done_event_id(completed_map: str) -> str:
        return f"{completed_map}{MapConfig.done_event_id()}"

    @staticmethod
    def next_map_string() -> str:
        return "next"

    @staticmethod
    def back_map_string() -> str:
        return "back"

    @staticmethod
    def world_map_prefix() -> str:
        return "w"

    @staticmethod
    def level_map_prefix() -> str:
        return "l"

    @staticmethod
    def expedition_map_prefix() -> str:
        return "expedition"

    @staticmethod
    def spaceship() -> str:
        return "spaceship"

    @staticmethod
    def hub_world() -> str:
        return "w0"

    @staticmethod
    def first_world() -> str:
        return "w1"

    @staticmethod
    def intro_level() -> str:
        return "l1v1"

    @staticmethod
    def test_level() -> str:
        return "l1v2"


class InstructionConfig:
    MAX_ABBREVIATION_LEN = 3


class QuantumSimulationConfig:
    DECIMALS = 3
    MAX_SPACE_PER_NUMBER = 1 + 1 + 1 + DECIMALS     # sign + "0" + "." + DECIMALS
    TOLERANCE = 0.1


class ShopConfig:
    @staticmethod
    def base_unit() -> int:
        return 1


class Config:   # todo make singleton and handle access to other configs?
    MAX_SEED = 1000000
    __VERSION = "v0.3.3"
    __GAME_CONFIG = "qrogue_game.config"
    __GAMEPLAY_HEAD = "[Gameplay]\n"
    __DEBUG = False

    __HEADER = "Qrogue "
    __SEED_HEAD = "Seed="
    __TIME_HEAD = "Time="
    __CONFIG_HEAD = "[Config]"

    @staticmethod
    def HEADER() -> str:
        return Config.__HEADER

    @staticmethod
    def SEED_HEAD() -> str:
        return Config.__SEED_HEAD

    @staticmethod
    def TIME_HEAD() -> str:
        return Config.__TIME_HEAD

    @staticmethod
    def CONFIG_HEAD() -> str:
        return Config.__CONFIG_HEAD

    @staticmethod
    def scientist_name() -> str:
        return "Robb"

    @staticmethod
    def player_name() -> str:
        return "Mike"

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
    def game_config_file() -> str:
        return Config.__GAME_CONFIG

    @staticmethod
    def debugging() -> bool:
        return Config.__DEBUG

    @staticmethod
    def debug_print(text: str):
        if Config.debugging():
            print(text)

    @staticmethod
    def activate_debugging():
        Config.__DEBUG = True

    @staticmethod
    def setup_user_data(custom_path: str = None):
        """
        Sets up the folder structure and default game config in the specified path.
        :param custom_path: where to store and load the user data (e.g. logs, save data)
        :return:
        """

        if custom_path:
            user_data_path = custom_path
        else:
            user_data_path = PathConfig.user_data_path()

        PathConfig.create_folder_structure(user_data_path)
        path = os.path.join(user_data_path, Config.__GAME_CONFIG)
        if not os.path.exists(path):
            text = ""
            text += Config.__GAMEPLAY_HEAD
            text += GameplayConfig.to_file_text()
            with open(path, "x") as file:
                file.write(text)

    @staticmethod
    def load():
        if not os.path.exists(PathConfig.user_data_path(Config.__GAME_CONFIG)):
            Config.setup_user_data()

        try:
            config = PathConfig.read(Config.__GAME_CONFIG, in_user_path=True)
        except FileNotFoundError:
            raise FileNotFoundError("Could not load the game's config file!")

        gameplay_start = config.index(Config.__GAMEPLAY_HEAD) + len(Config.__GAMEPLAY_HEAD)
        gameplay_end = len(config)
        if not GameplayConfig.from_log_text(config[gameplay_start:gameplay_end]):
            return 2

        return 0

    @staticmethod
    def save_gameplay_config() -> bool:
        text = f"{Config.__GAMEPLAY_HEAD}\n{GameplayConfig.to_file_text()}\n"
        PathConfig.write(Config.game_config_file(), text, in_user_path=True, may_exist=True, append=False)
        return True
