
import random
from game.map.navigation import *

P = 0   # player
A = 1
F = 7
E = 100 # empty field


class Map:
    def __init__(self, seed: int, width: int, height: int):
        rand = random.Random()
        rand.seed(seed)

        self.__player_pos = Coordinate(1, 1)

        self.__map = []
        for y in range(height):
            row = []
            for x in range(width):
                if y == 0 or y == height-1 or x == 0 or x == width-1:
                    row.append('#')
                else:
                    row.append(rand.randint(A, F))
            self.__map.append(row)

        self.__map[1][1] = P

    def height(self):
        return len(self.__map)

    def width(self):
        return len(self.__map[0])

    def at(self, x: int, y: int):
        if 0 <= y < len(self.__map) and 0 <= x < len(self.__map[y]):
            return self.__map[y][x]
        else:
            print("ERROR")

    def player_pos(self):
        return self.__player_pos

    def move_down(self):
        x, y = self.__player_pos.resolve()
        self.__player_pos = Coordinate(x, y + 1)
        self.__map[y][x] = E
        self.__map[y + 1][x] = P

    def move_right(self):
        x, y = self.__player_pos.resolve()
        self.__player_pos = Coordinate(x + 1, y)
        self.__map[y][x] = E
        self.__map[y][x + 1] = P

    # todo check bounds and add other directions