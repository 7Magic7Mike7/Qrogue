
from enum import Enum


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

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def opposite(self):
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


class Coordinate:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def resolve(self):
        return self.__x, self.__y

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        else:
            raise NotImplementedError(f"Adding \"{other}\" to a Coordinate is not supported!")

    def __sub__(self, other):
        if isinstance(other, Direction):
            return Coordinate(self.x - other.x, self.y - other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        else:
            raise NotImplementedError(f"Subtracting \"{other}\" from a Coordinate is not supported!")


def direction(c_from: Coordinate, c_to: Coordinate):
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


def distance(a: Coordinate, b: Coordinate):
    diff_x = a.x - b.x
    diff_y = a.y - b.y
    if diff_x < 0:
        diff_x = -diff_x
    if diff_y < 0:
        diff_y = -diff_y
    return diff_x + diff_y
