from typing import Callable, List

from qrogue.game.logic.actors import Boss, Enemy, Robot
from qrogue.game.world.map import LevelMap
from qrogue.game.world.navigation import Direction
from qrogue.util import Logger, ErrorConfig


class CallbackPack:
    __instance = None

    @staticmethod
    def dummy() -> "CallbackPack":
        return CallbackPack(start_level=lambda num, level: None, start_fight=lambda robot, enemy, direction: None,
                            start_boss_fight=lambda robot, boss, direction: None,
                            open_riddle=lambda robot, riddle: None, open_challenge=lambda robot, challenge: None,
                            visit_shop=lambda robot, shop_items: None, game_over=lambda: None)

    @staticmethod
    def reset():
        ErrorConfig.raise_deletion_exception()

    def __init__(self, start_level: "Callable[[int, LevelMap], None]",
                 start_fight: "Callable[[Robot, Enemy, Direction], None]",
                 start_boss_fight: "Callable[[Robot, Boss, Direction], None]",
                 open_riddle: "Callable[[Robot, Riddle], None]",
                 open_challenge: "Callable[[Robot, Challenge], None]",
                 visit_shop: "Callable[[Robot, List[ShopItem]], None]",
                 game_over: "Callable[[], None]"):
        self.__start_level = start_level
        self.__start_fight = start_fight
        self.__start_boss_fight = start_boss_fight
        self.__open_riddle = open_riddle
        self.__open_challenge = open_challenge
        self.__visit_shop = visit_shop
        self.__game_over = game_over

    @property
    def start_level(self) -> "Callable[[int, LevelMap], None]":
        return self.__start_level

    @property
    def start_fight(self) -> "Callable[[Robot, Enemy, Direction], None]":
        return self.__start_fight

    @property
    def start_boss_fight(self) -> "Callable[[Robot, Boss, Direction], None]":
        return self.__start_boss_fight

    @property
    def open_riddle(self):
        return self.__open_riddle

    @property
    def open_challenge(self):
        return self.__open_challenge

    @property
    def visit_shop(self):
        return self.__visit_shop

    @property
    def game_over(self):
        return self.__game_over
