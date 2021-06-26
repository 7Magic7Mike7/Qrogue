
import random
from enum import Enum

from game.actors.enemy import Enemy
from game.logic.qubit import Qubit
from game.map.navigation import Coordinate, Direction

P = 0   # player
A = 1
F = 7
E = 100 # empty field


class Tile(Enum):
    Empty = (0, " ", True)
    Player = (1, "P")
    Enemy = (10, "E")
    Wall = (100, "#")
    Obstacle = (110, "o")

    def __init__(self, code: int, img: str, walkable: bool = False):
        self.__code = code
        self.__img = img[0]
        self.__walkable = walkable

    @property
    def code(self):
        return self.__code

    @property
    def img(self):
        return self.__img

    def is_walkable(self):
        return self.__walkable


class Map:
    def __init__(self, seed: int, width: int, height: int):
        rand = random.Random()
        rand.seed(seed)

        self.__player_pos = Coordinate(2, 2)
        self.__enemy_pos = Coordinate(9, 9)

        self.__map = []
        for y in range(height):
            row = []
            for x in range(width):
                if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                    row.append(Tile.Wall)
                else:
                    if rand.randint(0, 7) == 1:
                        row.append(Tile.Obstacle)
                    else:
                        row.append(Tile.Empty)
            self.__map.append(row)

        self.__map[self.__player_pos.y][self.__player_pos.x] = Tile.Player
        self.__map[self.__enemy_pos.y][self.__enemy_pos.x] = Tile.Enemy
        self.__enemy = Enemy([Qubit(0, 3, 1), Qubit(1, 1, 3)])

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

        if self.__map[new_pos.y][new_pos.x].is_walkable():
            self.__player_pos = new_pos
            self.__map[y][x] = Tile.Empty
            self.__map[new_pos.y][new_pos.x] = Tile.Player
            return True
        else:
            return False

    def in_enemy_range(self):
        range_x = 2
        range_y = 2
        for x in range(self.__player_pos.x - range_x, self.__player_pos.x + range_x + 1):
            for y in range(self.__player_pos.y - range_y, self.__player_pos.y + range_y + 1):
                if 0 <= x < self.width() and 0 <= y < self.height():
                    tile = self.at(x, y)
                    if tile == Tile.Enemy:
                        return self.__enemy
        return None
