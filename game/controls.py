
from py_cui.keys import *


class Controls:
    def __init__(self):
        self.__move_up = KEY_UP_ARROW
        self.__move_right = KEY_RIGHT_ARROW
        self.__move_down = KEY_DOWN_ARROW
        self.__move_left = KEY_LEFT_ARROW

        self.__render = KEY_R_LOWER

    def move_up(self):
        return self.__move_up

    def move_right(self):
        return self.__move_right

    def move_down(self):
        return self.__move_down

    def move_left(self):
        return self.__move_left

    def render(self):
        return self.__render