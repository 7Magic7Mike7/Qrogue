from typing import List

from qrogue.game.logic.actors import Robot, Enemy, Boss, Riddle
from qrogue.game.logic.collectibles import ShopItem
from qrogue.game.world.map import CallbackPack
from qrogue.game.world.navigation import Direction
from qrogue.util import RandomManager, Config, PathConfig, Logger


def start_gp(args):
    print("started game")


def start_fight(robot: Robot, enemy: Enemy, direction: Direction):
    pass


def start_boss_fight(robot: Robot, boss: Boss, direction: Direction):
    pass


def open_riddle(robot: Robot, riddle: Riddle):
    pass


def visit_shop(robot: Robot, items: List[ShopItem]):
    pass


def load_map(map_name: str):
    print(f"Load map: {map_name}")


def game_over():
    print("game over")


def message_popup(title: str, text: str):
    print("----------------------------------------")
    print(f"[{title}]")
    print(text)
    print("----------------------------------------")


def error_popup(title: str, text: str):
    print("----------------------------------------")
    print(f"ERROR - {title}")
    print(text)
    print("----------------------------------------")


def init_singletons(seed: int = 7, include_config: bool = False, custom_data_path: str = None,
                    custom_user_path: str = None) -> bool:
    if include_config:
        if PathConfig.load_paths(custom_data_path, custom_user_path):
            return_code = Config.load()
            if return_code != 0:
                print(f"Error #{return_code}")
                return False
            Config.activate_debugging()
        else:
            print("Error! Could not load base paths.")
            return False

    Logger(seed)
    Logger.instance().set_popup(message_popup, error_popup)
    RandomManager(seed)  # initialize RandomManager
    CallbackPack(start_gp, start_fight, start_boss_fight, open_riddle, visit_shop, game_over)

    return True
