from game.actors.enemy import DummyEnemy
from game.map.tiles import *
from util.my_random import RandomManager as RM


class Room(ABC):
    INNER_WIDTH = 5                 # width inside the room, i.e. without walls and hallways
    INNER_HEIGHT = INNER_WIDTH      # height inside the room, i.e. without walls and hallways
    OUTER_WIDTH = INNER_WIDTH + 3   # width of the whole room area, i.e. with walls and hallways
    OUTER_HEIGHT = INNER_HEIGHT + 3 # height of the whole room area, i.e. with walls and hallways
    ROOM_WIDTH = INNER_WIDTH + 2    # width of the whole room, i.e. with walls but without hallways
    ROOM_HEIGHT = INNER_HEIGHT + 2  # height of the whole room, i.e. with walls but without hallways
    MID_X = int(ROOM_WIDTH / 2)     # middle of the room on the x-axis
    MID_Y = int(ROOM_HEIGHT / 2)    # middle of the room on the y-axis

    def __init__(self, tiles: "list of tiles", doors: "list of Doors"):
        self.__tiles = []
        top = [ Wall() for t in range(Room.ROOM_WIDTH) ]
        top.append(Void())
        self.__tiles.append(top)

        for y in range(Room.INNER_HEIGHT):
            row = [Wall()]
            for x in range(Room.INNER_WIDTH):
                if tiles is not None and len(tiles) > 0:
                    row.append(tiles.pop())    # todo is it okay to do this reversed?
                else:
                    row.append(Floor())
            row.append(Wall())
            row.append(Void())
            self.__tiles.append(row)

        room_bottom = [ Wall() for t in range(Room.ROOM_WIDTH) ]
        room_bottom.append(Void())
        bottom = [ Void() for t in range(Room.OUTER_WIDTH)]

        self.__tiles.append(room_bottom)
        self.__tiles.append(bottom)
        self.__doors = doors
        self.__is_visible = False
        self.__was_visited = False

        # North and West doors must be defined in the neighboring room, because that room creates the hallway
        # South and East doors are created and placed into a hallway
        for door in doors:
            if door.direction == Direction.North:
                self.__tiles[0][Room.MID_X] = Floor()
            elif door.direction == Direction.East:
                self.__tiles[Room.MID_Y-1][Room.ROOM_WIDTH] = Wall()
                self.__tiles[Room.MID_Y][Room.ROOM_WIDTH-1] = Floor()   # remove the wall in front of the hallway
                self.__tiles[Room.MID_Y][Room.ROOM_WIDTH] = door
                self.__tiles[Room.MID_Y+1][Room.ROOM_WIDTH] = Wall()
            elif door.direction == Direction.South:
                self.__tiles[Room.ROOM_HEIGHT][Room.MID_X-1] = Wall()
                self.__tiles[Room.ROOM_HEIGHT-1][Room.MID_X] = Floor()  # remove the wall in front of the hallway
                self.__tiles[Room.ROOM_HEIGHT][Room.MID_X] = door
                self.__tiles[Room.ROOM_HEIGHT][Room.MID_X+1] = Wall()
            elif door.direction == Direction.West:
                self.__tiles[Room.MID_Y][0] = Floor()

    def _set_tile(self, tile: Tile, x: int, y: int):
        if 0 <= x < Room.OUTER_WIDTH and 0 <= y < Room.OUTER_HEIGHT:
            self.__tiles[y][x] = tile
            return True
        return False

    def get_row(self, y: int):
        if 0 <= y < Room.OUTER_HEIGHT:
            row = []
            for x in range(len(self.__tiles[y])):
                row.append(self.at(x = x, y = y))
            return row
        else:
            return Room.OUTER_HEIGHT * [Invalid()]

    def at(self, x: int, y: int, force: bool = False):
        if 0 <= x < Room.OUTER_WIDTH and 0 <= y < Room.OUTER_HEIGHT:
            if self.__is_visible or force:
                return self.__tiles[y][x]
            elif x < Room.ROOM_WIDTH and y < Room.ROOM_HEIGHT:
                return FogOfWar()
            else:
                return Void()   # don't display possible hallways
        else:
            return Invalid()

    def enter(self):
        self.__is_visible = True
        self.__was_visited = True

    def leave(self, direction: Direction):
        test = 0


class SpawnRoom(Room):
    def __init__(self, tiles: "list of tiles", doors: "list of Doors", player: Player):    # todo add type to player; always spawn at center?
        super().__init__(tiles, doors)


class WildRoom(Room):
    def __init__(self, factory: EnemyFactory, tiles: "list of tiles", doors: "list of Doors"):

        self.__dictionary = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [] }
        if tiles is None or len(tiles) <= 0:
            tiles = []
            chance = 0.3
            for x in range(Room.INNER_WIDTH * Room.INNER_HEIGHT):
                if RM.instance().get() < chance:
                    enemy = DummyEnemy()
                    from game.game import GameHandler
                    id = RM.instance().get_int(min=0, max=10)
                    enemy = Enemy(factory, self.get_tiles_by_id, id)
                    if id > 0:
                        self.__dictionary[id].append(enemy)
                    tiles.append(enemy)
                else:
                    tiles.append(Floor())

        super().__init__(tiles, doors)

    def __str__(self):
        return "WR"

    def get_tiles_by_id(self, id: int):
        return self.__dictionary[id]


class GateRoom(Room):
    pass


class RiddleRoom(Room):
    pass


class ShopRoom(Room):
    pass


class TreasureRoom(Room):
    pass


class BossRoom(Room):
    def __init__(self, door: Door, boss: Boss, tiles: "list of tiles" = None):
        super().__init__(tiles, [door])
        self._set_tile(boss, x=Room.MID_X, y=Room.MID_Y)
