
import random
import sys

import py_cui.errors

from qrogue.game.logic.actors import Player
from qrogue.game.world.dungeon_generator import QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.game.world.navigation import Coordinate
from qrogue.management import GameHandler
from qrogue.util import Config, Logger, RandomManager


def __init_singletons(seed: int):
    Config.load(None)
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


def setup_game(data_path: str):
    Config.create(["Qrogue", data_path])


def start_game(config_location: str = None):
    __CONSOLE_ARGUMENT = "--from-console"
    __DEBUG_ARGUMENT = "--debug"

    return_code = Config.load(config_location)  # NEEDS TO BE THE FIRST THING WE DO!
    if return_code == 0:
        if __DEBUG_ARGUMENT in sys.argv:
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
        Logger.instance().flush()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the path is "
                  "valid please consider using another one without special characters.")

    if __CONSOLE_ARGUMENT not in sys.argv:
        print()
        input("[Qrogue] Press ENTER to close the application")

    exit(return_code)


def validate_map(path: str, is_level: bool = True, in_base_path: bool = True) -> bool:
    seed = 7
    __init_singletons(seed)

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
