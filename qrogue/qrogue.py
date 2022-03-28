
import random
import sys
from typing import Tuple, List

import py_cui.errors

from qrogue.game.logic.actors import Player
from qrogue.game.world.dungeon_generator import QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.game.world.navigation import Coordinate
from qrogue.management import GameHandler, SaveData
from qrogue.util import Config, Logger, RandomManager, PathConfig, GameplayConfig


def __init_singletons(seed: int):
    Config.load()
    Config.activate_debugging()

    def log_print(title: str, text: str):
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

    def visit_shop(robot, shop_item_list):
        pass

    def game_over():
        pass

    CallbackPack(start_level, start_fight, start_boss_fight, open_riddle, visit_shop, game_over)


def __parse_argument(argument: List[str], has_value: bool = False) -> Tuple[bool, str]:
    for arg in argument:
        if arg in sys.argv:
            if has_value:
                i = sys.argv.index(argument[0])
                if i + 1 < len(sys.argv):
                    return True, sys.argv[i + 1]
            else:
                return True, None
    return False, None


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


def start_game(data_folder: str = None, user_data_folder: str = None):
    __CONSOLE_ARGUMENT = ["--from-console", "-fc"]
    __DEBUG_ARGUMENT = ["--debug", "-d"]
    __GAME_DATA_PATH_ARGUMENT = ["--game-data", "-gd"]
    __USER_DATA_PATH_ARGUMENT = ["--user-data", "-ud"]

    exists, value = __parse_argument(__GAME_DATA_PATH_ARGUMENT, has_value=True)
    if exists:
        data_folder = value
    exists, value = __parse_argument(__USER_DATA_PATH_ARGUMENT, has_value=True)
    if exists:
        user_data_folder = value

    if PathConfig.load_paths(data_folder, user_data_folder):
        return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    else:
        return_code = 1
    if return_code == 0:
        if __parse_argument(__DEBUG_ARGUMENT)[0]:
            Config.activate_debugging()
        seed = random.randint(0, Config.MAX_SEED)
        print(f"[Qrogue] Starting game with seed = {seed}")
        try:
            game = GameHandler(seed)
            game.start()
        except py_cui.errors.PyCUIOutOfBoundsError:
            #print("[Qrogue] ERROR!")
            #print("Your terminal window is too small. "
            #      "Please make it bigger (i.e. maximize it) or reduce the font size.")
            print("---------------------------------------------------------")
            exit(1)

        # flush after the player stopped playing
        if GameplayConfig.auto_save():
            if SaveData.instance().save():
                print("[Qrogue] Successfully saved the game!")
            else:
                Logger.instance().error("Failed to save the game.", show=False)
        Logger.instance().flush()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the path is "
                  "valid please consider using another one without special characters.")

    if not __parse_argument(__CONSOLE_ARGUMENT)[0]:
        print()
        input("[Qrogue] Press ENTER to close the application")

    exit(return_code)


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

    if is_level:
        generator = QrogueLevelGenerator(seed, check_achievement, trigger_event, load_map)
    else:
        player = Player()
        generator = QrogueWorldGenerator(seed, player, check_achievement, trigger_event, load_map)

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
