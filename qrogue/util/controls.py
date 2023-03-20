from enum import IntEnum
from typing import List, Tuple, Callable

import py_cui.keys


# primary keys
_PK_UP = py_cui.keys.KEY_UP_ARROW
_PK_RIGHT = py_cui.keys.KEY_RIGHT_ARROW
_PK_DOWN = py_cui.keys.KEY_DOWN_ARROW
_PK_LEFT = py_cui.keys.KEY_LEFT_ARROW
_PK_CONFIRM = py_cui.keys.KEY_SPACE
_PK_CANCEL = py_cui.keys.KEY_BACKSPACE
_PK_SITUATIONAL1 = py_cui.keys.KEY_CTRL_LEFT
_PK_SITUATIONAL2 = py_cui.keys.KEY_CTRL_RIGHT
_PK_PAUSE = py_cui.keys.KEY_TAB
_PK_HELP = py_cui.keys.KEY_H_LOWER

# secondary keys (alternatives to primary keys)
_SK_UP = [py_cui.keys.KEY_W_LOWER]
_SK_RIGHT = [py_cui.keys.KEY_D_LOWER]
_SK_DOWN = [py_cui.keys.KEY_S_LOWER]
_SK_LEFT = [py_cui.keys.KEY_A_LOWER]
_SK_CONFIRM = [py_cui.keys.KEY_ENTER]
_SK_CANCEL = [py_cui.keys.KEY_SHIFT_LEFT, py_cui.keys.KEY_A_UPPER]
_SK_SITUATIONAL1 = [py_cui.keys.KEY_Q_LOWER]
_SK_SITUATIONAL2 = [py_cui.keys.KEY_E_LOWER]
_SK_PAUSE = [py_cui.keys.KEY_P_LOWER]
_SK_HELP = []   # no alternative

# hot keys (not needed for playing but can be helpful/increase convenience)
_HOT_KEYS = [
    [py_cui.keys.KEY_1],
    [py_cui.keys.KEY_2],
    [py_cui.keys.KEY_3],
    [py_cui.keys.KEY_4],
    [py_cui.keys.KEY_5],
    [py_cui.keys.KEY_6],
    [py_cui.keys.KEY_7],
    [py_cui.keys.KEY_8],
    [py_cui.keys.KEY_9],
    [py_cui.keys.KEY_0, 94],    # 94 = ^
]

# debug keys (not used in normal gameplay)
_DK_RERENDER = [py_cui.keys.KEY_CTRL_R]
_DK_PRINT_SCREEN = [py_cui.keys.KEY_CTRL_P]
_DK_CHEAT_INPUT = [py_cui.keys.KEY_CTRL_I]
_DK_CHEAT_LIST = [py_cui.keys.KEY_CTRL_L]
_DK_STOP_SIM = [py_cui.keys.KEY_ESCAPE]


class Keys(IntEnum):
    # 0 - 3
    MoveUp = 0
    MoveRight = MoveUp + 1
    MoveDown = MoveUp + 2
    MoveLeft = MoveUp + 3

    # 4 - 7
    SelectionUp = MoveLeft + 1
    SelectionRight = SelectionUp + 1
    SelectionDown = SelectionUp + 2
    SelectionLeft = SelectionUp + 3

    # 8 - 12
    PopupClose = SelectionLeft + 1
    PopupScrollUp = PopupClose + 1
    PopupScrollDown = PopupClose + 2
    PopupScrollUpFast = PopupClose + 3
    PopupScrollDownFast = PopupClose + 4

    # 13 - 18
    Help = PopupScrollDownFast + 1
    Action = Help + 1
    Cancel = Action + 1
    Situational1 = Cancel + 1
    Situational2 = Situational1 + 1

    Pause = Situational2 + 1

    # 19 - 28
    HotKey1 = Pause + 1
    HotKey2 = HotKey1 + 1
    HotKey3 = HotKey1 + 2
    HotKey4 = HotKey1 + 3
    HotKey5 = HotKey1 + 4
    HotKey6 = HotKey1 + 5
    HotKey7 = HotKey1 + 6
    HotKey8 = HotKey1 + 7
    HotKey9 = HotKey1 + 8
    HotKey0 = HotKey1 + 9

    # 29 - 31
    Render = HotKey0 + 1
    PrintScreen = Render + 1
    StopSimulator = PrintScreen + 1

    # 32 - 33
    CheatInput = StopSimulator + 1
    CheatList = CheatInput + 1

    # non valid keys
    Invalid = 100
    ErrorMarker = 101
    LevelBegin = 110

    @staticmethod
    def invalid_values() -> "List[Keys]":
        return [Keys.Invalid, Keys.ErrorMarker, Keys.LevelBegin]

    @staticmethod
    def selection_keys() -> "List[Keys]":
        return [Keys.SelectionUp, Keys.SelectionRight, Keys.SelectionDown, Keys.SelectionLeft]

    @staticmethod
    def main_keys() -> "List[Keys]":
        return Keys.selection_keys() + [Keys.Action, Keys.Cancel]

    @staticmethod
    def hotkeys() -> "List[Keys]":
        return [Keys.HotKey0, Keys.HotKey1, Keys.HotKey2, Keys.HotKey3, Keys.HotKey4, Keys.HotKey5, Keys.HotKey6,
                Keys.HotKey7, Keys.HotKey8, Keys.HotKey9]

    @staticmethod
    def from_code(code: int) -> "Keys":
        num = code - 1  # since code = num + 1
        return Keys.from_index(num)

    @staticmethod
    def from_index(index: int) -> "Keys":
        if index < len(Keys):
            for i, elem in enumerate(Keys):
                if i == index:
                    return elem
            # performance of above version might be better?
            # values = [elem for elem in Keys]
            # return values[index]
        else:
            values = Keys.invalid_values()
            if index < len(values):
                return values[index]
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
    INVALID_KEY = py_cui.keys.KEY_ALT_I     # is not allowed to be used as a valid key in the controls!
    __KEYS = [
        # move: 0 - 3
        [_PK_UP] + _SK_UP,
        [_PK_RIGHT] + _SK_RIGHT,
        [_PK_DOWN] + _SK_DOWN,
        [_PK_LEFT] + _SK_LEFT,
        # select: 4 - 7
        [_PK_UP] + _SK_UP,
        [_PK_RIGHT] + _SK_RIGHT,
        [_PK_DOWN] + _SK_DOWN,
        [_PK_LEFT] + _SK_LEFT,
        # popups: 8 - 13
        [_PK_CONFIRM] + _SK_CONFIRM,  #[KEY_ESCAPE],     # KEY_ESCAPE is not allowed to be at the first position because then the simulator would stop itself
        [_PK_UP] + _SK_UP,
        [_PK_RIGHT] + _SK_RIGHT,
        [_PK_DOWN] + _SK_DOWN,
        [_PK_LEFT] + _SK_LEFT,
        [_PK_HELP],
        # 14 - 18
        [_PK_CONFIRM] + _SK_CONFIRM,     # action
        [_PK_CANCEL] + _SK_CANCEL,  # cancel/back
        [_PK_SITUATIONAL1] + _SK_SITUATIONAL1,
        [_PK_SITUATIONAL2] + _SK_SITUATIONAL2,
        [_PK_PAUSE] + _SK_PAUSE,  # (Escape doesn't work here due to its special purpose for the engine)

        # special purpose hotkeys: 19 - 28
        _HOT_KEYS[0],  # Fight: Adapt (Add/Remove)
        _HOT_KEYS[1],  # Fight: Commit
        _HOT_KEYS[2],  # Fight: Reset
        _HOT_KEYS[3],  # Fight: Items
        _HOT_KEYS[4],  # Fight: Help
        _HOT_KEYS[5],  # Fight: Flee
        _HOT_KEYS[6],
        _HOT_KEYS[7],
        _HOT_KEYS[8],
        _HOT_KEYS[9],

        # debugging keys: 29 - 31
        _DK_RERENDER,  # render screen
        _DK_PRINT_SCREEN,   # print screen
        _DK_STOP_SIM,   # stop simulator
        # cheat keys: 32 - 33
        _DK_CHEAT_INPUT,   # cheat input
        _DK_CHEAT_LIST,   # cheat list
    ]

    def __init__(self, handle_key_presses: Callable[[int], None]):
        self.__handle_key_presses = handle_key_presses
        self.__pycui_keys = Controls.__KEYS.copy()

    def encode(self, key_pressed: int) -> Keys:
        """
        Converts a pressed key to an internal Key-representation that encodes the corresponding action
        :param key_pressed: the key that was pressed
        :return: an element of Key corresponding to the action executed by pressing key_pressed
        """
        for i in range(len(self.__pycui_keys)):
            if key_pressed in self.__pycui_keys[i]:
                return Keys.from_index(i)
        return Keys.Invalid

    def decode(self, key_code: int) -> Tuple[int, Keys]:
        """
        Decodes a code representation to a corresponding Keys element
        :param key_code: code representation of a Keys element
        :return: a keyboard key that can be pressed to trigger the corresponding action and its logical counterpart
        """
        if key_code == Keys.Invalid.code:
            return Controls.INVALID_KEY, Keys.Invalid
        key = Keys.from_code(key_code)
        return self.get_key(key), key

    def get_keys(self, key: Keys) -> List[int]:
        if key in Keys.invalid_values():
            return []
        return self.__pycui_keys[key.num]

    def get_key(self, key: Keys, index: int = 0) -> int:
        if key in Keys.invalid_values():
            return Controls.INVALID_KEY
        keys = self.get_keys(key)
        if 0 <= index < len(keys):
            return keys[index]
        return keys[0]

    def get_hotkey(self, number: int) -> List[int]:
        if number == 0:
            number = 10     # 0 is after 9, so at the 10th position
        base = Keys.HotKey1.num - 1
        return self.__pycui_keys[base + number]

    def handle(self, key: Keys):
        key_pressed = self.get_key(key)
        self.__handle_key_presses(key_pressed)

    @property
    def action(self) -> List[int]:
        return self.__pycui_keys[Keys.Action.num]
