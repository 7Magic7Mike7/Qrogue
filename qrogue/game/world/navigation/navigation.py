
from enum import Enum
from typing import List

from qrogue.util import Logger


class Direction(Enum):
    Center = (0, 0)

    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)
    N = North
    E = East
    S = South
    W = West

    Up = North
    Right = East
    Down = South
    Left = West
    U = Up
    R = Right
    D = Down
    L = Left

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @staticmethod
    def from_coordinates(c_from: "Coordinate", c_to: "Coordinate") -> "Direction":
        return direction(c_from, c_to)

    @staticmethod
    def values() -> List["Direction"]:
        return [Direction.North, Direction.East, Direction.South, Direction.West]

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def is_horizontal(self) -> bool:
        """

        :return: True if direction is East or West, False otherwise
        """
        return self.x != 0

    def opposite(self) -> "Direction":
        if self == Direction.North:
            return Direction.South
        elif self == Direction.East:
            return Direction.West
        elif self == Direction.South:
            return Direction.North
        elif self == Direction.West:
            return Direction.East
        else:
            return Direction.Center

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, Coordinate):
            return other + self
        else:
            Logger.instance().throw(NotImplementedError(f"Adding \"{other}\" to a Coordinate is not supported!"))


class Coordinate:
    @staticmethod
    def distance(a: "Coordinate", b: "Coordinate") -> int:
        return abs(a.x - b.x) + abs(a.y - b.y)

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def resolve(self) -> (int, int):
        return self.__x, self.__y

    def linearize(self, row_width: int) -> int:
        """
        Returns the index this Coordinate would have if it was stored in a row-wise fashion in a 1D array.

        :param row_width: width of one row of the grid stored in a corresponding 1D array
        :return:
        """
        return self.x + self.y * row_width

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        else:
            Logger.instance().throw(NotImplementedError(f"Adding \"{other}\" to a Coordinate is not supported!"))

    def __sub__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x - other.x, self.y - other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        else:
            Logger.instance().throw(NotImplementedError(f"Subtracting \"{other}\" from a Coordinate is not supported!"))

    def __eq__(self, other) -> bool:
        if isinstance(other, Coordinate):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return 61 * self.x + 51 * self.y

    def __str__(self):
        return f"({self.__x}|{self.__y})"


def direction(c_from: Coordinate, c_to: Coordinate) -> Direction:
    diff = c_to - c_from
    if diff.x == 0 and diff.y == 0:
        return Direction.Center
    if abs(diff.x) > abs(diff.y):
        if diff.x > 0:
            return Direction.East
        else:
            return Direction.West
    else:
        if diff.y > 0:
            return Direction.South
        else:
            return Direction.North


def distance(a: Coordinate, b: Coordinate) -> int:
    diff_x = a.x - b.x
    diff_y = a.y - b.y
    if diff_x < 0:
        diff_x = -diff_x
    if diff_y < 0:
        diff_y = -diff_y
    return diff_x + diff_y
