
import random

A = 1
F = 7

class Map:
    def __init__(self, seed: int, width: int, height: int):
        rand = random.Random()
        rand.seed(seed)

        self.__map = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(rand.randint(A, F))
            self.__map.append(row)

    def at(self, x: int, y: int):
        if 0 <= y and y < len(self.__map) and 0 <= x and x < len(self.__map[y]):
            return self.__map[y][x]
        else:
            print("ERROR")

    def height(self):
        return len(self.__map)

    def width(self):
        return len(self.__map[0])