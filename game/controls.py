
from py_cui.keys import *


class Controls:
    def __init__(self):
        self.__move_up = KEY_UP_ARROW
        self.__move_right = KEY_RIGHT_ARROW
        self.__move_down = KEY_DOWN_ARROW
        self.__move_left = KEY_LEFT_ARROW

        self.__selection_up = KEY_UP_ARROW
        self.__selection_right = KEY_RIGHT_ARROW
        self.__selection_down = KEY_DOWN_ARROW
        self.__selection_left = KEY_LEFT_ARROW

        self.__render = KEY_R_LOWER

    @property
    def move_up(self):
        return self.__move_up

    @property
    def move_right(self):
        return self.__move_right

    @property
    def move_down(self):
        return self.__move_down

    @property
    def move_left(self):
        return self.__move_left

    @property
    def selection_up(self):
        return self.__selection_up

    @property
    def selection_right(self):
        return self.__selection_right

    @property
    def selection_down(self):
        return self.__selection_down

    @property
    def selection_left(self):
        return self.__selection_left


    def render(self):
        return self.__render