from typing import Callable, List

from qrogue.game.logic.actors import Boss, Enemy, Robot, Riddle, Challenge
from qrogue.game.world.navigation import Direction


class CallbackPack:
    @staticmethod
    def dummy() -> "CallbackPack":
        return CallbackPack(start_fight=lambda robot, enemy, direction: None,
                            start_boss_fight=lambda robot, boss, direction: None,
                            open_riddle=lambda robot, riddle: None, open_challenge=lambda robot, challenge: None,
                            game_over=lambda: None)

    def __init__(self, start_fight: Callable[[Robot, Enemy, Direction], None],
                 start_boss_fight: Callable[[Robot, Boss, Direction], None],
                 open_riddle: Callable[[Robot, Riddle], None],
                 open_challenge: Callable[[Robot, Challenge], None],
                 game_over: Callable[[], None]):
        self.__start_fight = start_fight
        self.__start_boss_fight = start_boss_fight
        self.__open_riddle = open_riddle
        self.__open_challenge = open_challenge
        self.__game_over = game_over

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
    def open_challenge(self):
        return self.__open_challenge

    @property
    def game_over(self):
        return self.__game_over
