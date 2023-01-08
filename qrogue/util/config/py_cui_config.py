import py_cui
from py_cui.errors import PyCUIOutOfBoundsError


class PyCuiConfig:
    KEY_ESCAPE = py_cui.keys.KEY_ESCAPE
    KEY_CTRL_Q = py_cui.keys.KEY_CTRL_Q

    OutOfBoundsError = PyCUIOutOfBoundsError
    PyCuiWidget = py_cui.widgets.Widget


class PyCuiColors:
    BLACK_ON_WHITE = py_cui.BLACK_ON_WHITE
    BLACK_ON_RED = py_cui.BLACK_ON_RED

    BLUE_ON_BLACK = py_cui.BLUE_ON_BLACK
    BLUE_ON_WHITE = py_cui.BLUE_ON_WHITE

    CYAN_ON_BLACK = py_cui.CYAN_ON_BLACK

    GREEN_ON_BLACK = py_cui.GREEN_ON_BLACK
    GREEN_ON_WHITE = py_cui.GREEN_ON_WHITE

    MAGENTA_ON_BLACK = py_cui.MAGENTA_ON_BLACK
    MAGENTA_ON_WHITE = py_cui.MAGENTA_ON_WHITE

    RED_ON_BLACK = py_cui.RED_ON_BLACK
    RED_ON_BLUE = py_cui.RED_ON_BLUE
    RED_ON_WHITE = py_cui.RED_ON_WHITE

    WHITE_ON_BLACK = py_cui.WHITE_ON_BLACK
    WHITE_ON_CYAN = py_cui.WHITE_ON_CYAN
    WHITE_ON_GREEN = py_cui.WHITE_ON_GREEN

    YELLOW_ON_BLACK = py_cui.YELLOW_ON_BLACK
