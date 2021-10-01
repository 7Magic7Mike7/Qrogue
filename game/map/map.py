
import random

import game.map.tiles as tiles
from game.actors.boss import DummyBoss
from game.actors.factory import EnemyFactory
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, SpawnRoom, BossRoom, WildRoom
from util.config import MapConfig
from util.logger import Logger


class Map:
    WIDTH = 5
    HEIGHT = 5

    def __init__(self, seed: int, width: int, height: int, player: tiles.Player, start_fight_callback):
        rand = random.Random()
        rand.seed(seed)
        self.__player = player  # TODO save player_pos in player?
        self.__start_fight_callback = start_fight_callback
        self.__enemy_factory = EnemyFactory(self.__start_fight_callback)

        if MapConfig.create_random():
            for y in range(height):
                row = []
                for x in range(width):
                    if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                        row.append(tiles.Wall())
                    else:
                        if rand.randint(0, 7) == 1:
                            row.append(tiles.Obstacle())
                        else:
                            row.append(tiles.Floor())
                self.__player_pos = Coordinate(2, 3)
                self.__enemy_pos = Coordinate(9, 9)
        else:
            self.__build_room_layout(self.__player)

    def __build_room_layout(self, player: tiles.Player):
        spawn = SpawnRoom([], [tiles.Door(Direction.East), tiles.Door(Direction.South)], player)
        spawn_x = 0
        spawn_y = 0

        self.rooms = [[None for x in range(Map.WIDTH)] for y in range(Map.HEIGHT)]
        self.rooms[spawn_x][spawn_y] = spawn
        self.rooms[0][1] = BossRoom(tiles.Door(Direction.West), tiles.Boss(DummyBoss(), self.__start_fight_callback))
        self.rooms[1][0] = WildRoom(self.__enemy_factory, tiles=None, doors=[tiles.Door(Direction.North)])

        self.__cur_room = spawn
        self.__player_pos = Map.__calculate_pos(Coordinate(spawn_x, spawn_y), Coordinate(Room.MID_X, Room.MID_Y))
        self.__cur_room.enter()

    def __get_room(self, x: int, y: int):
        room_x = int(x / Room.OUTER_WIDTH)
        room_y = int(y / Room.OUTER_HEIGHT)
        pos_x = int(x % Room.OUTER_WIDTH)
        pos_y = int(y % Room.OUTER_HEIGHT)

        return self.rooms[room_y][room_x], Coordinate(x=pos_x, y=pos_y)

    @staticmethod
    def __calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate):
        y = pos_of_room.y * Room.OUTER_HEIGHT + pos_in_room.y
        x = pos_of_room.x * Room.OUTER_WIDTH + pos_in_room.x
        return Coordinate(x, y)

    @property
    def height(self):
        return Map.HEIGHT * Room.OUTER_HEIGHT

    @property
    def width(self):
        return Map.WIDTH * Room.OUTER_WIDTH

    def row_width(self, y: int):    # determine the right most room (for rendering)
        val = 0
        if 0 <= y < Map.HEIGHT:
            for x in range(Map.WIDTH):
                if self.rooms[y][x] is not None:
                    val = x
        return val

    def at(self, x: int, y: int, force: bool = False):
        if x == self.__player_pos.x and y == self.__player_pos.y:
            return self.__player

        if 0 <= x < self.width and 0 <= y < self.height:
            room, pos = self.__get_room(x=x, y=y)
            if room is None:
                return tiles.Void()
            else:
                return room.at(x=pos.x, y=pos.y, force=force)
        else:
            Logger.instance().error(f"Error! Invalid position: {x}|{y}")
            return tiles.Invalid()

    @property
    def player_pos(self):
        return self.__player_pos

    @property
    def player(self) -> tiles.Player:
        return self.__player

    def move(self, direction: Direction):
        new_pos = self.__player_pos + direction

        if new_pos.y < 0 or self.height <= new_pos.y or \
                new_pos.x < 0 or self.width <= new_pos.x:
            return False

        tile = self.at(x=new_pos.x, y=new_pos.y, force=True)
        if tile.is_walkable(direction, self.__player.player):
            room, pos = self.__get_room(new_pos.x, new_pos.y)
            if room != self.__cur_room: # todo what if room is None?
                self.__cur_room.leave(direction)
                self.__cur_room = room
                self.__cur_room.enter()

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.on_walk(direction, self.player.player)

            self.__player_pos = new_pos
            return True
        else:
            return False
