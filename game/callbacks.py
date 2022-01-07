from game.actors.enemy import Enemy
from game.actors.robot import Robot
from game.map.navigation import Direction


class SimpleCallback:
    def __call__(self, *args: None, **kwargs: dict) -> None:
        pass


class OnWalkCallback:
    def __call__(self, *args: (Robot, Enemy, Direction), **kwds: dict) -> None:
        pass


class SelectionCallback:
    def __call__(self, *args: None, **kwargs: dict) -> bool:
        pass


class CallbackPack:
    def __init__(self, start_gameplay: "(Map)", start_fight: "(Robot, Enemy, Direction)",
                 start_boss_fight: "(Robot, Boss, Direction)", open_riddle: "(Robot, Riddle)",
                 visit_shop: "(Robot, list of ShopItems"):
        self.__start_gameplay = start_gameplay
        self.__start_fight = start_fight
        self.__start_boss_fight = start_boss_fight
        self.__open_riddle = open_riddle
        self.__visit_shop = visit_shop

    @property
    def start_gameplay(self):
        return self.__start_gameplay

    @property
    def start_fight(self):
        return self.__start_fight

    @property
    def start_boss_fight(self):
        return self.__start_boss_fight

    @property
    def open_riddle(self):
        return self.__open_riddle

    @property
    def visit_shop(self):
        return self.__visit_shop
