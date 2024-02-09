from typing import Callable, Tuple

import py_cui
from py_cui.errors import PyCUIOutOfBoundsError


class PyCuiConfig:
    # 0 is used as default since it isn't a valid width or height otherwise
    __get_dimensions: Callable[[], Tuple[int, int]] = lambda: (0, 0)

    @staticmethod
    def get_min_dimensions() -> Tuple[int, int]:
        """

        Returns: minimum number of rows and columns needed to display the game correctly

        """
        # retrieved by trial and error
        # 133 is the minimum width to fully display a 2-qubit puzzle without visual errors
        # 31 can be explained like this: Our PyCUI has 10 rows, so there can be 10 widgets per column. To display a
        # widget correctly, PyCUI needs at least three character-rows - 1x upper border, 1x content, 1x lower border.
        # Hence, one PyCUI row corresponds to at least three character-rows. Therefore, we need at least 30 character-
        # rows to display all widgets. Furthermore, one row is needed to display the title bar. The result is a minimum
        # of 31 rows. We're not sure whether that is exactly how PyCUI works under the hood, but it makes sense and
        # everything below 31 rows throws an internal error complaining about the height being too small.
        return 31, 133

    @staticmethod
    def set_get_dimensions_callback(get_dimensions: Callable[[], Tuple[int, int]]):
        PyCuiConfig.__get_dimensions = get_dimensions

    @staticmethod
    def get_dimensions() -> Tuple[int, int]:
        return PyCuiConfig.__get_dimensions()

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
    WHITE_ON_MAGENTA = py_cui.WHITE_ON_MAGENTA

    YELLOW_ON_BLACK = py_cui.YELLOW_ON_BLACK
