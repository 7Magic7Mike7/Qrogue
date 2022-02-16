from typing import Callable

from game.actors.boss import Boss
from game.actors.enemy import Enemy
from game.actors.robot import Robot
from game.map.level_map import LevelMap
from game.map.navigation import Direction


class CallbackPack:
    def __init__(self, start_level: Callable[[int, LevelMap], None],
                 start_fight: Callable[[Robot, Enemy, Direction], None],
                 start_boss_fight: Callable[[Robot, Boss, Direction], None],
                 open_riddle: "(Robot, Riddle)",
                 visit_shop: "(Robot, list of ShopItems"):
        self.__start_level = start_level
        self.__start_fight = start_fight
        self.__start_boss_fight = start_boss_fight
        self.__open_riddle = open_riddle
        self.__visit_shop = visit_shop

    @property
    def start_level(self) -> Callable[[int, LevelMap], None]:
        return self.__start_level

    @property
    def start_fight(self) -> Callable[[Robot, Enemy, Direction], None]:
        return self.__start_fight

    @property
    def start_boss_fight(self) -> Callable[[Robot, Boss, Direction], None]:
        return self.__start_boss_fight

    @property
    def open_riddle(self):
        return self.__open_riddle

    @property
    def visit_shop(self):
        return self.__visit_shop
