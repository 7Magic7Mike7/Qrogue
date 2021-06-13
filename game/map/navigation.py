
from enum import Enum


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


class Direction(Enum):
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

    # @property
    # def c(self):
    #    return Coordinate(self.__x, self.__y)
