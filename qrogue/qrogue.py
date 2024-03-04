
import random
import sys
from typing import Tuple, List, Optional

from qrogue.game.logic.actors import Player
from qrogue.game.world.dungeon_generator import QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.game.world.navigation import Coordinate
from qrogue.management import SaveData, QrogueCUI
from qrogue.util import PyCuiConfig, Config, Logger, RandomManager, PathConfig, GameplayConfig
from qrogue.util.key_logger import OverWorldKeyLogger


def __init_singletons(seed: int):
    Config.load()
    Config.activate_debugging()

    def log_print(title: str, text: str, position: Optional[int] = None):
        #print(f"\"{title}\": {text}")
        pass

    def log_print_error(title: str, text: str):
        log_print(f"Error - {title}", text)

    Logger(seed)
    Logger.instance().set_popup(log_print, log_print_error)

    RandomManager(seed)

    def start_level(num, level):
        pass

    def start_fight(robot, enemy, direction):
        pass

    def start_boss_fight(robot, boss, direction):
        pass

    def open_riddle(robot, riddle):
        pass

    def open_challenge(robot, challenge):
        pass

    def visit_shop(robot, shop_item_list):
        pass

    def game_over():
        pass

    CallbackPack(start_level, start_fight, start_boss_fight, open_riddle, open_challenge, visit_shop, game_over)


def __parse_argument(argument: List[str], has_value: bool = False) -> Tuple[bool, Optional[str]]:
    for arg in argument:
        if arg in sys.argv:
            if has_value:
                i = sys.argv.index(arg)
                if i + 1 < len(sys.argv):
                    return True, sys.argv[i + 1]
            else:
                return True, None
    return False, None


def start_qrogue() -> int:
    Logger.print_to_console("Loading...")     # notify player that the game is loading

    __CONSOLE_ARGUMENT = ["--from-console", "-fc"]
    __DEBUG_ARGUMENT = ["--debug", "-d"]
    __SEED_ARGUMENT = ["--seed", "-s"]                      # seed argument
    __TEST_LEVEL_ARGUMENT = ["--test-level", "-tl"]
    __GAME_DATA_PATH_ARGUMENT = ["--game-data", "-gd"]  # path argument
    __USER_DATA_PATH_ARGUMENT = ["--user-data", "-ud"]  # path argument
    # __CONTROLS_ARGUMENT = ["--controls", "-c"]          # int argument
    __SIMULATION_FILE_ARGUMENT = ["--simulation-path", "-sp"]   # path argument
    __VALIDATE_MAP_ARGUMENT = ["--validate-map", "-vm"]     # path argument
    __PLAY_LEVEL_ARGUMENT = ["--play-level", "-pl"]     # str argument

    from_console, _ = __parse_argument(__CONSOLE_ARGUMENT)
    debugging, _ = __parse_argument(__DEBUG_ARGUMENT)
    test_level, _ = __parse_argument(__TEST_LEVEL_ARGUMENT)
    _, data_folder = __parse_argument(__GAME_DATA_PATH_ARGUMENT, has_value=True)
    _, user_data_folder = __parse_argument(__USER_DATA_PATH_ARGUMENT, has_value=True)
    has_simulation_path, simulation_path = __parse_argument(__SIMULATION_FILE_ARGUMENT, has_value=True)
    has_map_path, map_path = __parse_argument(__VALIDATE_MAP_ARGUMENT, has_value=True)
    _, seed = __parse_argument(__SEED_ARGUMENT, has_value=True)
    has_play_level, level2play = __parse_argument(__PLAY_LEVEL_ARGUMENT, has_value=True)

    if has_map_path:
        if validate_map(map_path):
            return 0
        else:
            return 1
    else:
        if has_simulation_path:
            return simulate_game(simulation_path, from_console, debugging, data_folder, user_data_folder)
        elif has_play_level:
            return play_level(level2play, debugging, data_folder, seed)
        else:
            return start_game(from_console, debugging, test_level, data_folder, user_data_folder, seed)


def setup_game(game_data_path: str = "", user_data_path: str = "") -> None:
    """
    Creates the needed folder structure and game config file qrogue_game.config if not already existent.

    :param game_data_path: the path where we want to setup the game data
    :param user_data_path: the path where we want to load and store the user data (e.g. logs, save data)
    :return: None
    """
    Config.setup_user_data(user_data_path)

    path = PathConfig.launch_config_path()
    data = "\n"
    data += f"{game_data_path}\n"
    data += f"{user_data_path}\n"
    PathConfig.write(path, data, in_user_path=False, may_exist=True, append=False)


def start_game(from_console: bool = False, debugging: bool = False, test_level: bool = False,
               data_folder: str = None, user_data_folder: str = None, seed: str = None) -> int:
    if PathConfig.load_paths(data_folder, user_data_folder):
        return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    else:
        return_code = 1
    if return_code == 0:
        if debugging:
            Config.activate_debugging(test_level)

        if seed is not None and not debugging:
            print("[Qrogue] Attention! Manual seeds are only available in debug-mode!")
        if seed is None or not debugging:
            seed = random.randint(0, Config.MAX_SEED)
        else:
            seed = int(seed)
        print(f"[Qrogue] Starting game with seed = {seed}")
        try:
            QrogueCUI(seed).start()
        except PyCuiConfig.OutOfBoundsError:
            #print("[Qrogue] ERROR!")
            #print("Your terminal window is too small. "
            #      "Please make it bigger (i.e. maximize it) or reduce the font size.")
            print("---------------------------------------------------------")
            input("[Qrogue] Press ENTER to close the application")
            sys.exit(1)

        # flush after the player stopped playing
        if GameplayConfig.auto_save():
            success, message = SaveData.instance().save()
            if success:
                print("[Qrogue] Successfully saved the game!")
            else:
                Logger.instance().error(f"Failed to save the game: {message.text}", show=False, from_pycui=False)
        Logger.instance().flush()
        OverWorldKeyLogger.instance().flush_if_useful()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the "
                  "path is valid please consider using another one without special characters.")

    if not from_console:
        print()
        input("[Qrogue] Press ENTER to close the application")

    return return_code


def simulate_game(simulation_path: str, from_console: bool = False, debugging: bool = False, data_folder: str = None,
                  user_data_folder: str = None) -> int:
    if PathConfig.load_paths(data_folder, user_data_folder):
        return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    else:
        return_code = 1
    if return_code == 0:
        if debugging:
            Config.activate_debugging()

        print(f"[Qrogue] Simulating the game recorded at \"{simulation_path}\"")
        try:
            QrogueCUI.start_simulation(simulation_path)
        except PyCuiConfig.OutOfBoundsError:
            # print("[Qrogue] ERROR!")
            # print("Your terminal window is too small. "
            #      "Please make it bigger (i.e. maximize it) or reduce the font size.")
            print("---------------------------------------------------------")
            sys.exit(1)

        # flush after the player stopped playing
        if GameplayConfig.auto_save():
            success, message = SaveData.instance().save()
            if success:
                print("[Qrogue] Successfully saved the game!")
            else:
                Logger.instance().error(f"Failed to save the game: {message.text}", show=False, from_pycui=False)
        Logger.instance().flush()
        OverWorldKeyLogger.instance().flush_if_useful()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the "
                  "path is valid please consider using another one without special characters.")

    if not from_console:
        print()
        input("[Qrogue] Press ENTER to close the application")

    return return_code


def validate_map(path: str, is_level: bool = True, in_base_path: bool = True) -> bool:
    seed = 7
    try:
        __init_singletons(seed)
    except Exception as ex:
        print(f"Error: {ex}")
        print("Most likely you used validate_map() while also running the game which is forbidden. Make sure to "
              "validate maps separately!")
        return False

    def check_achievement(achievement: str) -> bool:
        return False

    def trigger_event(event: str):
        pass

    def load_map(map_name: str, spawn_pos: Coordinate):
        pass

    def show_message(title: str, text: str, reopen: Optional[bool], position: Optional[int]):
        pass

    if is_level:
        generator = QrogueLevelGenerator(seed, check_achievement, trigger_event, load_map, show_message)
    else:
        player = Player()
        generator = QrogueWorldGenerator(seed, player, check_achievement, trigger_event, load_map, show_message)

    try:
        error_occurred = False
        generator.generate(path, in_base_path)
    except FileNotFoundError as fnf:
        error_occurred = True
        print(f"Could not find specified file! Error: {fnf}")
    except SyntaxError as se:
        error_occurred = True
        print("Found syntax error!")
        print(se)

    return not error_occurred


def play_level(level_name: str, debugging: bool = False, data_folder: str = None, seed: str = None) -> int:
    # NOTE: This does not reset or set any achievements! Therefore, the level might not play the same as if you would
    # play it normally for the first time.
    if PathConfig.load_paths(data_folder, None):
        return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    else:
        return_code = 1
    if return_code == 0:
        if seed is not None and not debugging:
            print("[Qrogue] Attention! Manual seeds are only available in debug-mode!")
        if seed is None or not debugging:
            seed = random.randint(0, Config.MAX_SEED)
        else:
            seed = int(seed)
        if debugging: Config.activate_debugging()
        print(f"[Qrogue] Starting level {level_name} with seed = {seed}")
        try:
            QrogueCUI(seed).start(level_name)
        except PyCuiConfig.OutOfBoundsError:
            print("---------------------------------------------------------")
            input("[Qrogue] Press ENTER to close the application")
            sys.exit(1)

        # flush after the player stopped playing
        Logger.instance().flush()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the "
                  "path is valid please consider using another one without special characters.")
    return return_code
