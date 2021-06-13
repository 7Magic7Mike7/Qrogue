
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
                if y == 0 or y == height - 1 or x == 0 or x == width - 1:
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

    def move(self, dir: Direction):
        x, y = self.__player_pos.resolve()
        new_pos = Coordinate(x + dir.x, y + dir.y)

        if new_pos.y < 0 or len(self.__map) <= new_pos.y or \
                new_pos.x < 0 or len(self.__map[0]) <= new_pos.x:
            return False

        self.__player_pos = new_pos
        self.__map[y][x] = E
        self.__map[new_pos.y][new_pos.x] = P
        return True
