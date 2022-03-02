from enum import IntEnum
from typing import List

from py_cui.keys import *


class Keys(IntEnum):
    MoveUp = 0
    MoveRight = MoveUp + 1
    MoveDown = MoveUp + 2
    MoveLeft = MoveUp + 3

    SelectionUp = MoveLeft + 1
    SelectionRight = SelectionUp + 1
    SelectionDown = SelectionUp + 2
    SelectionLeft = SelectionUp + 3

    PopupClose = SelectionLeft + 1
    PopupScrollUp = PopupClose + 1
    PopupScrollDown = PopupClose + 2

    Action = PopupScrollDown + 1
    Cancel = Action + 1
    Pause = Cancel + 1

    HotKey1 = Pause + 1
    HotKey2 = Pause + 2
    HotKey3 = Pause + 3
    HotKey4 = Pause + 4
    HotKey5 = Pause + 5
    HotKey6 = Pause + 6
    HotKey7 = Pause + 7
    HotKey8 = Pause + 8
    HotKey9 = Pause + 9
    HotKey0 = Pause + 10

    Render = HotKey0 + 1
    PrintScreen = Render + 1
    StopSimulator = PrintScreen + 1

    CheatInput = StopSimulator + 1
    CheatList = CheatInput + 1

    Invalid = 126

    @staticmethod
    def from_code(code: int) -> "Keys":
        num = code - 1  # since code = num + 1
        return Keys.from_index(num)

    @staticmethod
    def from_index(index: int) -> "Keys":
        i = 0
        for elem in Keys:
            if i == index:
                return elem
            i += 1
        return Keys.Invalid

    def __init__(self, num):
        self.__num = num

    @property
    def num(self) -> int:
        return self.__num

    @property
    def code(self) -> int:
        # must be a valid char
        return self.__num + 1

    def to_char(self) -> str:
        return chr(self.code)


class Controls:
    INVALID_KEY = Keys.Invalid.num

    def __init__(self):
        self.__pycui_keys = [
            # move
            [KEY_UP_ARROW, KEY_W_LOWER],
            [KEY_RIGHT_ARROW, KEY_D_LOWER],
            [KEY_DOWN_ARROW, KEY_S_LOWER],
            [KEY_LEFT_ARROW, KEY_A_LOWER],
            # select
            [KEY_UP_ARROW, KEY_W_LOWER],
            [KEY_RIGHT_ARROW, KEY_D_LOWER],
            [KEY_DOWN_ARROW, KEY_S_LOWER],
            [KEY_LEFT_ARROW, KEY_A_LOWER],
            # popups
            [KEY_ESCAPE, KEY_SPACE, KEY_ENTER],
            [KEY_UP_ARROW, KEY_W_LOWER],
            [KEY_DOWN_ARROW, KEY_S_LOWER],

            [KEY_SPACE, KEY_ENTER],     # action
            [KEY_BACKSPACE, KEY_A_UPPER, KEY_SHIFT_LEFT],  # cancel/back
            [KEY_P_LOWER, KEY_TAB],  # pause    (Escape doesn't work here due to its special purpose for the engine)

            # special purpose hotkeys
            [KEY_1],  # Fight: Adapt (Add/Remove)
            [KEY_2],  # Fight: Commit
            [KEY_3],  # Fight: Reset
            [KEY_4],  # Fight: Items
            [KEY_5],  # Fight: Help
            [KEY_6],  # Fight: Flee
            [KEY_7],
            [KEY_8],
            [KEY_9],
            [KEY_0, 94],    # 94 = ^

            [KEY_CTRL_R],  # render screen
            [KEY_CTRL_P],   # print screen
            [KEY_ESCAPE],   # stop simulator
            [KEY_CTRL_I],   # cheat input
            [KEY_CTRL_L],   # cheat list
        ]

    def encode(self, key_pressed: int) -> Keys:
        """
        Converts a pressed key to an internal Key-representation that encodes the corresponding action
        :param key_pressed: the key that was pressed
        :return: an element of Key corresponding to the action executed by pressing key_pressed
        """
        for i in range(len(self.__pycui_keys)):
            if key_pressed == self.__pycui_keys[i]:
                return Keys.from_index(i)
        return Keys.Invalid

    def decode(self, key_code: int) -> int:
        """
        Decodes a code representation to a corresponding Keys element
        :param key_code: code representation of a Keys element
        :return: a keyboard key that can be pressed to trigger the corresponding action
        """
        if key_code == Keys.Invalid.code:
            return None
        key = Keys.from_code(key_code)
        return self.get_key(key)

    def get_keys(self, key: Keys) -> List[int]:
        return self.__pycui_keys[key.num]

    def get_key(self, key: Keys, index: int = 0):
        keys = self.get_keys(key)
        if 0 <= index < len(keys):
            return keys[index]
        return keys[0]

    @property
    def action(self) -> List[int]:
        return self.__pycui_keys[Keys.Action.num]


class Pausing:
    __instance = None

    @staticmethod
    def pause():
        if Pausing.__instance is not None:
            Pausing.__instance.__pause_now()

    def __init__(self, callback: "()"):
        self.__callback = callback
        Pausing.__instance = self

    def __pause_now(self):
        self.__callback()
