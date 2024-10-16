import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Callable, Optional, Tuple, Union

from qrogue.game import target_factory
from qrogue.game.logic import Message
from qrogue.game.logic.actors import Robot, Riddle
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import Enemy as EnemyTile, Tile, Floor, Decoration, Teleport, FogOfWar, Void, Invalid, \
    Door, Wall, HallwayEntrance, Riddler, Challenger, Boss, Collectible, Message as MessageTile
from qrogue.util import CommonQuestions, MapConfig, Logger, CheatConfig, RandomManager


class AreaType(Enum):
    Invalid = -1
    Placeholder = 0
    Hallway = 1
    EmptyRoom = 2
    MetaRoom = 3

    SpawnRoom = 10
    WildRoom = 11       # contains mostly normal Enemies/Puzzles
    # ShopRoom = 12
    RiddleRoom = 13     # room is built around its Riddle(s)
    GateRoom = 14       # room contains mainly a Gate and other Tiles to support it
    BossRoom = 15       # room contains a Boss-Puzzle and other supporting Tiles
    TreasureRoom = 16   # room contains mainly some sort of Treasure/special Pickup and supporting Tiles
    ChallengeRoom = 17  # room is built around its Challenge(s)
    PauseRoom = 18      # room doesn't contain much interactive Tiles, mainly some Energy pickups
    StoryRoom = 19      # room is mainly there for story purposes, e.g. containing Messages
    PhantomRoom = 20    # a special hidden room that cannot be accessed via normal means (e.g. only via tunneling)

    @staticmethod
    def values(include_pseudo_areas: Optional[bool] = None, only_rooms: Optional[bool] = None) -> List["AreaType"]:
        if include_pseudo_areas is None:  # todo: method is not used
            include_pseudo_areas = False
        if only_rooms is None:
            only_rooms = True

        areas = [AreaType.SpawnRoom, AreaType.WildRoom, AreaType.RiddleRoom, AreaType.GateRoom,
                 AreaType.BossRoom, AreaType.TreasureRoom]
        if not only_rooms:
            areas += [AreaType.Hallway]
        if include_pseudo_areas:
            areas += [AreaType.Invalid, AreaType.Placeholder, AreaType.EmptyRoom, AreaType.MetaRoom]
        return areas


class Area(ABC):
    __ID = 1
    __FOG = FogOfWar()
    __VOID = Void()
    UNIT_WIDTH = MapConfig.room_width()
    UNIT_HEIGHT = MapConfig.room_height()
    MID_X = MapConfig.room_mid_x()
    MID_Y = MapConfig.room_mid_y()

    @staticmethod
    def void() -> Void:
        return Area.__VOID

    def __init__(self, type_: AreaType, tile_matrix: "list[list[Tile]]"):
        self.__id = Area.__ID
        Area.__ID += 1

        self.__type = type_
        self.__tiles = tile_matrix
        self.__width = len(tile_matrix[0])
        self.__height = len(tile_matrix)

        self.__is_in_sight = False
        self.__is_visible = False
        self.__was_visited = False

    @property
    def id(self) -> int:
        return self.__id

    @property
    def is_visible(self) -> bool:
        return self.__is_visible or CheatConfig.revealed_map()

    @property
    def _is_visible_value(self) -> bool:
        return self.__is_visible

    @property
    def is_in_sight(self) -> bool:
        return self.__is_in_sight

    @property
    def type(self) -> AreaType:
        return self.__type

    def _set_tile(self, tile: Tile, x: int, y: int) -> bool:
        """

        :param tile: the Tile we want to place
        :param x: horizontal position of the Tile
        :param y: vertical position of the Tile
        :return: whether we could place the Tile at the given position or not
        """
        if 0 <= x < Area.UNIT_WIDTH and 0 <= y < Area.UNIT_HEIGHT:
            self.__tiles[y][x] = tile
            return True
        return False

    def at(self, x: int, y: int, force: bool = False) -> Tile:
        """

        :param x: horizontal position of the Tile we want to know
        :param y: vertical position of the Tile we want to know
        :param force: whether we return the real Tile or not (e.g. invisible Rooms usually return Fog)
        :return: the Tile at the requested position
        """
        if 0 <= x < self.__width and 0 <= y < self.__height:
            if self.is_visible or force:
                return self.__tiles[y][x]
            else:
                if self.is_in_sight:
                    return Area.__FOG
                else:
                    return Area.void()
        else:
            return Invalid()

    def get_row_str(self, row: int) -> str:
        if row >= len(self.__tiles):
            return "".join([Invalid().get_img()] * Area.UNIT_WIDTH)

        if self.is_visible:
            tiles = [t.get_img() for t in self.__tiles[row]]
            return "".join(tiles)
        elif self.is_in_sight:
            fog_str = Area.__FOG.get_img()
            return fog_str * self.__width
        else:
            void_str = Area.__VOID.get_img()
            return void_str * self.__width

    def make_visible(self):
        self.__is_in_sight = True
        self.__is_visible = True

    def in_sight(self):
        self.__is_in_sight = True

    def enter(self, direction: Direction):
        self.__is_visible = True
        self.__was_visited = True

    def leave(self, direction: Direction):
        pass

    def __str__(self):
        return "?"


class Hallway(Area):
    @staticmethod
    def is_first(direction: Direction):
        """
        Determines whether a Hallway in the Direction direction from the perspective of a room is the first or second
        Room of the Hallway
        :param direction: Direction from Room to Hallway
        :return: True if Hallway is to the East or South of Room, false otherwise
        """
        return direction in [Direction.East, Direction.South]

    def __init__(self, door: Door):
        self.__door = door
        self.__hide = door.is_event_locked
        self.__room1: Optional[Room] = None
        self.__room2: Optional[Room] = None
        if self.is_horizontal():
            missing_half = int((Area.UNIT_WIDTH - 3) / 2)
            row: List[Tile] = [Void()] * missing_half + [Wall(), door, Wall()] + [Void()] * missing_half
            super(Hallway, self).__init__(AreaType.Hallway, [row])
        else:
            missing_half = int((Area.UNIT_HEIGHT - 3) / 2)
            tiles: List[List[Tile]] = [[Void()]] * missing_half + [[Wall()], [door], [Wall()]] + [
                [Void()]] * missing_half
            super(Hallway, self).__init__(AreaType.Hallway, tiles)

    @property
    def door(self) -> Door:
        return self.__door

    def set_room(self, room: "Room", direction: Direction):
        """

        :param room:
        :param direction:  in which Direction the Hallways is from room's point of view
        :return:
        """
        if Hallway.is_first(direction):
            self.__room1 = room
        else:
            self.__room2 = room

    def connects_horizontally(self) -> bool:
        """

        :return: whether the Hallway connects two Rooms horizontally or not
        """
        return self.__door.direction.is_horizontal()

    def is_horizontal(self) -> bool:
        """

        :return: True if the Hallway is a row, False if it is a column
        """
        return not self.connects_horizontally()

    def make_visible(self):
        super(Hallway, self).make_visible()
        r1id, r2id = None, None
        if self.__room1:
            r1id = self.__room1.id
            self.__room1.in_sight()
        if self.__room2:
            r2id = self.__room2.id
            self.__room2.in_sight()

        if r1id is None and r2id is None:
            Logger.instance().debug(f"#hw{self.id}: room1 and room2 is None!", from_pycui=False)
        elif r1id is None:
            Logger.instance().debug(f"#hw{self.id}: room2=#r{r2id} but room1 is None!", from_pycui=False)
        elif r2id is None:
            Logger.instance().debug(f"#hw{self.id}: room1=#r{r1id} but room2 is None!", from_pycui=False)

    def get_row_str(self, row: int) -> str:
        if self.__hide:
            if self.__door.check_event():
                if self.__room1.is_visible or self.__room2.is_visible:
                    self.make_visible()
                # elif self.__room1.in_sight or self.__room2.in_sight:
                #    self.in_sight()
                self.__hide = False
        return super(Hallway, self).get_row_str(row)

    def in_sight(self):
        if not self.__hide:
            self.make_visible()

    def enter(self, direction: Direction):
        self.__room1.make_visible()
        self.__room2.make_visible()

    def room(self, first: bool):
        if first:
            return self.__room1
        else:
            return self.__room2

    def __str__(self) -> str:
        if self.is_horizontal():
            orientation = "-"
        else:
            orientation = "|"
        return f"HW{self.id}: {self.__room1} {orientation} {self.__room2}"


class Room(Area):
    INNER_WIDTH = Area.UNIT_WIDTH - 2  # width inside the room, i.e. without walls and hallways
    INNER_HEIGHT = Area.UNIT_HEIGHT - 2  # height inside the room, i.e. without walls and hallways
    INNER_MID_X = int(INNER_WIDTH / 2)
    INNER_MID_Y = int(INNER_HEIGHT / 2)

    @staticmethod
    def _set(tile_list: List[Tile], x: int, y: int, tile: Tile) -> bool:
        index = y * Room.INNER_WIDTH + x
        if 0 <= index < len(tile_list):
            tile_list[index] = tile
            return True
        return False

    @staticmethod
    def mid(inner: bool = True) -> Coordinate:
        if inner:
            return Coordinate(Room.INNER_MID_X, Room.INNER_MID_Y)
        else:
            return Coordinate(Area.MID_X, Area.MID_Y)

    @staticmethod
    def coordinate_to_index(pos: Union[Coordinate, Tuple[int, int]], in_room: bool = True) -> int:
        """

        :param pos: either Coordinate or Tuple of x and y position
        :param in_room: whether pos is given as in-room position or not (i.e. skip ring of walls or not)
        :return: index of a row-based tile list corresponding to the given position
        """
        if in_room:
            width = Room.INNER_WIDTH
        else:
            width = Room.UNIT_WIDTH
        if isinstance(pos, Coordinate):
            x, y = pos.x, pos.y
        else:
            x, y = pos
        return x + y * width

    @staticmethod
    def index_to_coordinate(index: int, in_room: bool = True) -> Coordinate:
        """

        :param index: index of a row-based tile list
        :param in_room: whether index is given as in-room position or not (i.e. skip ring of walls or not)
        :return: position corresponding to the given index of a row-based tile list
        """
        if in_room:
            width, height = Room.INNER_WIDTH, Room.INNER_HEIGHT
        else:
            width, height = Room.UNIT_WIDTH, Room.UNIT_HEIGHT
        assert 0 <= index < width * height, f"Index = {index} out of range: [0, {width * height}["
        return Coordinate(index % width, int(index / width))

    @staticmethod
    def direction_to_hallway_entrance_pos(direction: Direction, in_room: bool = True) -> Coordinate:
        """

        :param direction: side of the room where the hallway entrance is
        :param in_room: whether the return value is an in-room position or not (i.e. skip ring of walls or not)
        :return:
        """
        if in_room:
            # we have to use adapted middles since there is no ring of walls yet
            in_room_mid_x = Room.MID_X - 1
            in_room_mid_y = Room.MID_Y - 1
        else:
            in_room_mid_x = Room.MID_X
            in_room_mid_y = Room.MID_Y
        # up and left destructively interfere with +1, resulting in 0
        # while right and bottom constructively interfere with +1, resulting in 2
        return Coordinate(in_room_mid_x * (1 + direction.x), in_room_mid_y * (1 + direction.y))

    @staticmethod
    def get_empty_room_tile_list() -> "list of Tiles":
        return [Floor()] * (Room.INNER_WIDTH * Room.INNER_HEIGHT)

    @staticmethod
    def dic_to_tile_list(tile_dic: Dict[Coordinate, Tile]) -> List[Tile]:
        tile_list = Room.get_empty_room_tile_list()
        if tile_dic:
            for coordinate, tile in tile_dic.items():
                index = Room.coordinate_to_index(coordinate)
                if 0 <= index < len(tile_list):
                    tile_list[index] = tile
                else:
                    Logger.instance().throw(IndexError(f"Invalid Index ({index} for tile_list of length "
                                                       f"{len(tile_list)}!"))
        return tile_list

    def __init__(self, type_: AreaType, tile_list: List[Tile], north_hallway: Optional[Hallway] = None,
                 east_hallway: Optional[Hallway] = None, south_hallway: Optional[Hallway] = None,
                 west_hallway: Optional[Hallway] = None):
        tiles: List[List[Tile]] = []
        room_top = [Wall()] * Area.UNIT_WIDTH
        tiles.append(room_top)

        # fence the room tiles with Walls
        for y in range(Room.INNER_HEIGHT):
            row = [Wall()]
            for x in range(Room.INNER_WIDTH):
                if tile_list is not None:
                    index = x + y * Room.INNER_WIDTH
                    if index < len(tile_list):
                        row.append(tile_list[index])
                    else:
                        row.append(Floor())
                else:
                    row.append(Floor())
            row.append(Wall())
            tiles.append(row)

        room_bottom = [Wall()] * Area.UNIT_WIDTH
        tiles.append(room_bottom)

        self.__hallways: Dict[Direction, Hallway] = {}
        if north_hallway is not None and not north_hallway.connects_horizontally():
            tiles[0][Area.MID_X] = HallwayEntrance(north_hallway.door)
            self.__hallways[Direction.North] = north_hallway
            north_hallway.set_room(self, Direction.North)

        if east_hallway is not None and east_hallway.connects_horizontally():
            tiles[Area.MID_Y][Area.UNIT_WIDTH - 1] = HallwayEntrance(east_hallway.door)
            self.__hallways[Direction.East] = east_hallway
            east_hallway.set_room(self, Direction.East)

        if south_hallway is not None and not south_hallway.connects_horizontally():
            tiles[Area.UNIT_HEIGHT - 1][Area.MID_X] = HallwayEntrance(south_hallway.door)
            self.__hallways[Direction.South] = south_hallway
            south_hallway.set_room(self, Direction.South)

        if west_hallway is not None and west_hallway.connects_horizontally():
            tiles[Area.MID_Y][0] = HallwayEntrance(west_hallway.door)
            self.__hallways[Direction.West] = west_hallway
            west_hallway.set_room(self, Direction.West)

        super(Room, self).__init__(type_, tiles)

    def _set_hallway(self, north_hallway: Hallway = None, east_hallway: Hallway = None, south_hallway: Hallway = None,
                     west_hallway: Hallway = None):
        if north_hallway is not None and not north_hallway.connects_horizontally():
            self._set_tile(Floor(), Area.MID_X, 0)
            self.__hallways[Direction.North] = north_hallway
            north_hallway.set_room(self, Direction.North)

        if east_hallway is not None and east_hallway.connects_horizontally():
            self._set_tile(Floor(), Area.UNIT_WIDTH - 1, Area.MID_Y)
            self.__hallways[Direction.East] = east_hallway
            east_hallway.set_room(self, Direction.East)

        if south_hallway is not None and not south_hallway.connects_horizontally():
            self._set_tile(Floor(), Area.MID_X, Area.UNIT_HEIGHT - 1)
            self.__hallways[Direction.South] = south_hallway
            south_hallway.set_room(self, Direction.South)

        if west_hallway is not None and west_hallway.connects_horizontally():
            self._set_tile(Floor(), 0, Area.MID_Y)
            self.__hallways[Direction.West] = west_hallway
            west_hallway.set_room(self, Direction.West)

    def get_hallway(self, direction: Direction, throw_error: bool = True) -> Optional[Hallway]:
        if direction in self.__hallways:
            return self.__hallways[direction]
        elif throw_error:
            dic = [(str(self.__hallways[k]) + "\n") for k in self.__hallways]
            Logger.instance().error(f"Invalid hallway access for {self}:\n{direction} not in {dic}", show=False,
                                    from_pycui=False)
        return None

    def make_visible(self):
        super(Room, self).make_visible()
        for key in self.__hallways:
            hallway = self.__hallways[key]
            hallway.in_sight()

    def at(self, x: int, y: int, force: bool = False, inside_only: bool = False) -> Tile:
        """

        :param x: horizontal position of the Tile we want to know
        :param y: vertical position of the Tile we want to know
        :param force: whether we return the real Tile or not (e.g. invisible Rooms usually return Fog)
        :param inside_only: whether we consider the whole room or only its content inside the static walls; interprets
                            x and y accordingly
        :return: the Tile at the requested position
        """
        if inside_only:
            if 0 <= x < Room.INNER_WIDTH and 0 <= y < Room.INNER_HEIGHT:
                # offset position by 1
                return super(Room, self).at(x + 1, y + 1, force)
            return Invalid()
        else:
            return super(Room, self).at(x, y, force)

    @abstractmethod
    def abbreviation(self) -> str:
        pass

    def to_string(self) -> str:
        text = str(self) + "\n"
        for y in range(Area.UNIT_HEIGHT):
            for x in range(Area.UNIT_WIDTH):
                tile = self.at(x, y, force=True)
                text += tile.get_img()
            text += "\n"
        return text

    def __str__(self) -> str:
        return self.abbreviation() + str(self.id)


class CopyAbleRoom(Room, ABC):
    @abstractmethod
    def copy(self, hw_dic: Dict[Direction, Hallway]) -> "CopyAbleRoom":
        pass


class MetaRoom(CopyAbleRoom):
    def __init__(self, load_map_callback: Callable[[str], None], orientation: Direction, message: Message,
                 level_to_load: str, mtype: str, num: int, blocking: bool = True, north_hallway: Hallway = None,
                 east_hallway: Hallway = None, south_hallway: Hallway = None, west_hallway: Hallway = None,
                 is_spawn: bool = False):
        self.__load_map_callback = load_map_callback
        self.__orientation = orientation
        self.__message = message
        self.__level_to_load = level_to_load
        self.__mtype = mtype
        self.__num = num
        self.__blocking = blocking
        self.__is_spawn = is_spawn

        if is_spawn and False:  # todo not used/wanted currently, maybe add back later
            super(MetaRoom, self).__init__(AreaType.MetaRoom, Room.get_empty_room_tile_list(), north_hallway,
                                           east_hallway, south_hallway, west_hallway)
        else:
            if blocking:
                if orientation.is_horizontal():
                    dash_decoration = Decoration('|')
                else:
                    dash_decoration = Decoration('-')
            else:
                dash_decoration = Floor()  # ignore it for non-blocking since it might be placed in front of a hallway

            type_decoration = Decoration(mtype)
            num_decoration = Decoration(str(num)[0])

            tile_list = Room.get_empty_room_tile_list()
            msg_tile = MessageTile(self.__message, -1)
            level_tile = Teleport(self.__load_map_callback, level_to_load, None)

            if orientation is Direction.North:
                self._set(tile_list, 0, 0, type_decoration)
                self._set(tile_list, Room.INNER_MID_X, 0, dash_decoration)
                self._set(tile_list, Room.INNER_WIDTH - 1, 0, num_decoration)
                self._set(tile_list, 0, Room.INNER_HEIGHT - 1, msg_tile)
                self._set(tile_list, Room.INNER_WIDTH - 1, Room.INNER_HEIGHT - 1, level_tile)
                coordinate = Coordinate(0, Room.INNER_MID_Y - 1)
                addition = Direction.East

            elif orientation is Direction.East:
                self._set(tile_list, Room.INNER_WIDTH - 1, 0, type_decoration)
                self._set(tile_list, Room.INNER_WIDTH - 1, Room.INNER_MID_Y, dash_decoration)
                self._set(tile_list, Room.INNER_WIDTH - 1, Room.INNER_HEIGHT - 1, num_decoration)
                self._set(tile_list, 0, 0, msg_tile)
                self._set(tile_list, 0, Room.INNER_HEIGHT - 1, level_tile)
                coordinate = Coordinate(Room.INNER_MID_X + 1, 0)
                addition = Direction.South

            elif orientation is Direction.South:
                self._set(tile_list, 0, Room.INNER_HEIGHT - 1, type_decoration)
                self._set(tile_list, Room.INNER_MID_X, Room.INNER_HEIGHT - 1, dash_decoration)
                self._set(tile_list, Room.INNER_WIDTH - 1, Room.INNER_HEIGHT - 1, num_decoration)
                self._set(tile_list, 0, 0, msg_tile)
                self._set(tile_list, Room.INNER_WIDTH - 1, 0, level_tile)
                coordinate = Coordinate(0, Room.INNER_MID_Y + 1)
                addition = Direction.East

            elif orientation is Direction.West:
                self._set(tile_list, 0, 0, type_decoration)
                self._set(tile_list, 0, Room.INNER_MID_Y, dash_decoration)
                self._set(tile_list, 0, Room.INNER_HEIGHT - 1, num_decoration)
                self._set(tile_list, Room.INNER_WIDTH - 1, 0, msg_tile)
                self._set(tile_list, Room.INNER_WIDTH - 1, Room.INNER_HEIGHT - 1, level_tile)
                coordinate = Coordinate(Room.INNER_MID_X - 1, 0)
                addition = Direction.South

            else:
                raise SyntaxError(f"Invalid orientation for Hallway: {orientation}.")

            if blocking:
                counter = 0
                while counter < 5 and self._set(tile_list, coordinate.x, coordinate.y, Wall()):
                    coordinate += addition
                    counter += 1
            super(MetaRoom, self).__init__(AreaType.MetaRoom, tile_list, north_hallway, east_hallway, south_hallway,
                                           west_hallway)

    def abbreviation(self) -> str:
        return "MR"

    def copy(self, hw_dic: Dict[Direction, Hallway]) -> CopyAbleRoom:
        # if we wouldn't copy it we could very easily get errors because the hallways
        # will be set for all the layout positions that reference this room and hence
        # can ultimately lead to non-existing rooms
        if hw_dic:
            new_room = MetaRoom(self.__load_map_callback, self.__orientation, self.__message, self.__level_to_load,
                                self.__mtype, self.__num, self.__blocking, hw_dic[Direction.North],
                                hw_dic[Direction.East], hw_dic[Direction.South], hw_dic[Direction.West],
                                self.__is_spawn)
        else:
            raise SyntaxError("Room without hallway!")

        if self._is_visible_value:
            # don't use Room's implementation but Area's
            super(CopyAbleRoom, new_room).make_visible()
        elif self.is_in_sight:
            new_room.in_sight()
        return new_room


class CustomRoom(CopyAbleRoom):
    def __init__(self, type_: AreaType, tile_matrix: Optional[List[List[Tile]]],
                 north_hallway: Optional[Hallway] = None, east_hallway: Optional[Hallway] = None,
                 south_hallway: Optional[Hallway] = None, west_hallway: Optional[Hallway] = None):
        self.__tile_matrix = tile_matrix
        tile_list = []
        for row in tile_matrix:
            tile_list += row
        super(CustomRoom, self).__init__(type_, tile_list, north_hallway, east_hallway, south_hallway, west_hallway)

    def abbreviation(self) -> str:
        return "CR"

    def copy(self, hw_dic: Dict[Direction, Hallway]) -> CopyAbleRoom:
        # if we wouldn't copy it we could very easily get errors because the hallways
        # will be set for all the layout positions that reference this room and hence
        # can ultimately lead to non-existing rooms
        if hw_dic:
            new_room = CustomRoom(self.type, self.__tile_matrix, hw_dic[Direction.North], hw_dic[Direction.East],
                                  hw_dic[Direction.South], hw_dic[Direction.West])
        else:
            # todo not sure if rooms without hallways should be legal
            new_room = CustomRoom(self.type, self.__tile_matrix)

        if self._is_visible_value:
            # don't use Room's implementation but Area's
            super(Room, new_room).make_visible()
        elif self.is_in_sight:
            new_room.in_sight()
        return new_room


class EmptyRoom(CopyAbleRoom):
    def __init__(self, hw_dic: Dict[Direction, Hallway]):
        north_hallway = None
        if Direction.North in hw_dic:
            north_hallway = hw_dic[Direction.North]

        east_hallway = None
        if Direction.East in hw_dic:
            east_hallway = hw_dic[Direction.East]

        south_hallway = None
        if Direction.South in hw_dic:
            south_hallway = hw_dic[Direction.South]

        west_hallway = None
        if Direction.West in hw_dic:
            west_hallway = hw_dic[Direction.West]

        super(EmptyRoom, self).__init__(AreaType.EmptyRoom, Room.get_empty_room_tile_list(), north_hallway,
                                        east_hallway, south_hallway, west_hallway)

    def abbreviation(self) -> str:
        return "ER"

    def copy(self, hw_dic: Dict[Direction, Hallway]) -> "CopyAbleRoom":
        return EmptyRoom(hw_dic)


class SpecialRoom(Room, ABC):
    # todo check if it should still apply that SpecialRooms can only have one Hallway - adapt Astar in LayoutGenerator
    #  if that changes!
    #  answering thoughts after some time: If they can have multiple entrances/exits Key placement gets much harder
    #  we could not simply place keys in non-special rooms but would also have to check if 1st key is reachable from
    #  SpawnRoom, 2nd key from SpawnRoom and one special room, ...
    def __init__(self, type_: AreaType, hallway: Hallway, direction: Direction, special_tile: Tile,
                 tile_dic: Optional[Dict[Coordinate, Tile]] = None):
        """

        :param hallway:
        :param direction: the Direction to the Hallway based on the Room's perspective
        :param special_tile: the tile this room is dedicated to, placed in the middle
        :param tile_dic:
        """
        if tile_dic is None: tile_dic = {}
        tile_dic[Room.mid()] = special_tile
        tile_list = Room.dic_to_tile_list(tile_dic)
        if Hallway.is_first(direction):
            if hallway.connects_horizontally():
                super(SpecialRoom, self).__init__(type_, tile_list, east_hallway=hallway)
            else:
                super(SpecialRoom, self).__init__(type_, tile_list, south_hallway=hallway)
        else:
            if hallway.connects_horizontally():
                super(SpecialRoom, self).__init__(type_, tile_list, west_hallway=hallway)
            else:
                super(SpecialRoom, self).__init__(type_, tile_list, north_hallway=hallway)


class SpawnRoom(CopyAbleRoom):
    def __init__(self, leave_map_callback: Callable[[], None],
                 tile_dic: Dict[Coordinate, Tile] = None, north_hallway: Hallway = None, east_hallway: Hallway = None,
                 south_hallway: Hallway = None, west_hallway: Hallway = None, place_teleporter: bool = True):
        room_mid = Coordinate(Room.INNER_MID_X, Room.INNER_MID_Y)
        if tile_dic is None:
            tile_dic = {}
        else:
            if room_mid in tile_dic and place_teleporter:
                Logger.instance().error("Specified tile_dic with non-empty room-center for SpawnRoom. Overriding it "
                                        "with Teleporter.", show=False, from_pycui=False)
        if place_teleporter:
            tile_dic[room_mid] = Teleport(self.__teleport_callback, MapConfig.back_map_string(), None)
        self.__tile_dic = tile_dic
        super(SpawnRoom, self).__init__(AreaType.SpawnRoom, Room.dic_to_tile_list(tile_dic), north_hallway,
                                        east_hallway, south_hallway, west_hallway)
        self.__leave_map = leave_map_callback
        self.__is_done = None

    def abbreviation(self):
        return "SR"

    def set_is_done_callback(self, is_done_callback: Callable[[], bool]):
        self.__is_done = is_done_callback

    def __teleport_callback(self, level_to_load: str, room: Optional[Coordinate]):
        if self.__is_done:
            if self.__is_done():
                self.__conditional_going_back(0)
            else:
                CommonQuestions.GoingBack.ask(self.__conditional_going_back)
        else:
            Logger.instance().error("is_done_callback not set yet!", show=False, from_pycui=False)

    def __conditional_going_back(self, confirmed: int):
        if confirmed == 0:
            self.__leave_map()

    def copy(self, hw_dic: Dict[Direction, Hallway]) -> "CopyAbleRoom":
        # don't place a teleporter because it's already in tile_dic if it should be placed
        return SpawnRoom(self.__leave_map, self.__tile_dic, hw_dic[Direction.North], hw_dic[Direction.East],
                         hw_dic[Direction.South], hw_dic[Direction.West], place_teleporter=False)


class BaseWildRoom(Room):
    def __init__(self, tile_list: List[Tile], get_tiles_by_id: Callable[[int], List[Tile]],
                 north_hallway: Optional[Hallway] = None, east_hallway: Optional[Hallway] = None,
                 south_hallway: Optional[Hallway] = None, west_hallway: Optional[Hallway] = None):
        self.get_tiles_by_id = get_tiles_by_id
        super(BaseWildRoom, self).__init__(AreaType.WildRoom, tile_list, north_hallway, east_hallway, south_hallway,
                                           west_hallway)

    def abbreviation(self):
        return "WR"


class WildRoom(BaseWildRoom):
    __NUM_OF_ENEMY_GROUPS = 4

    def __init__(self, factory: target_factory.EnemyFactory, chance: float = 0.6, north_hallway: Hallway = None,
                 east_hallway: Hallway = None, south_hallway: Hallway = None, west_hallway: Hallway = None):
        from qrogue.util import Config
        Config.check_reachability("WildRoom()")
        self.__dictionary = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        rm = RandomManager.create_new(7)

        available_positions = []
        for y in range(Room.INNER_HEIGHT):
            available_positions += [Coordinate(x, y) for x in range(Room.INNER_WIDTH)]
        num_of_enemies = len(available_positions) * chance
        if rm.get_bool(msg="WR_enemyPlacementRounding"):
            num_of_enemies = math.floor(num_of_enemies)
        else:
            num_of_enemies = math.ceil(num_of_enemies)

        # here we could add other stuff (pickups, buttons?, ...) to the room and adapt available_positions accordingly

        tile_list = Room.get_empty_room_tile_list()
        for i in range(num_of_enemies):
            eid = rm.get_int(min_=0, max_=WildRoom.__NUM_OF_ENEMY_GROUPS + 1, msg="WildRoom_eid")
            enemy = EnemyTile(factory, self.__get_tiles_by_id, self.__update_entangled_tiles, eid)
            if eid > 0:
                self.__dictionary[eid].append(enemy)
            pos = rm.get_element(available_positions, remove=True, msg="WildRoom_epos")
            tile_list[Room.coordinate_to_index(pos)] = enemy

        super().__init__(tile_list, self.__get_tiles_by_id, north_hallway, east_hallway, south_hallway, west_hallway)

    def __get_tiles_by_id(self, eid: int) -> List[EnemyTile]:
        return self.__dictionary[eid]

    def __update_entangled_tiles(self, enemy: EnemyTile):
        self.__dictionary[enemy.eid].append(enemy)


class DefinedWildRoom(BaseWildRoom):
    def __init__(self, tile_list: List[Tile], north_hallway: Hallway = None, east_hallway: Hallway = None,
                 south_hallway: Hallway = None, west_hallway: Hallway = None):
        self.__dictionary = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        for tile in tile_list:
            # 0s always collapse to "fight" so they don't need to be in the dictionary for entanglement
            if isinstance(tile, EnemyTile) and tile.eid > 0:
                self.__dictionary[tile.eid].append(tile)
        super().__init__(tile_list, self.__get_tiles_by_id, north_hallway=north_hallway, east_hallway=east_hallway,
                         south_hallway=south_hallway, west_hallway=west_hallway)

    def __get_tiles_by_id(self, id_: int) -> List[EnemyTile]:
        return self.__dictionary[id_]


class TreasureRoom(SpecialRoom):
    def __init__(self, treasure: Union[Collectible, Instruction], hallway: Hallway, direction: Direction,
                 tile_dic: Dict[Coordinate, Tile] = None):
        if isinstance(treasure, Instruction):
            super().__init__(AreaType.GateRoom, hallway, direction, Collectible(treasure, force_add=True), tile_dic)
        else:
            super().__init__(AreaType.TreasureRoom, hallway, direction, treasure, tile_dic)

    def abbreviation(self) -> str:
        return "TR"


class ChallengeRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, direction: Direction, challenger: Challenger,
                 tile_dic: Dict[Coordinate, Tile] = None):
        super().__init__(AreaType.ChallengeRoom, hallway, direction, challenger, tile_dic)

    def abbreviation(self) -> str:
        return "TR"


class RiddleRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, direction: Direction, riddle: Riddle,
                 open_riddle_callback: Callable[[Robot, Riddle], None], tile_dic: Dict[Coordinate, Tile] = None):
        super().__init__(AreaType.RiddleRoom, hallway, direction, Riddler(open_riddle_callback, riddle), tile_dic)

    def abbreviation(self):
        return "RR"


class BossRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, direction: Direction, boss: Boss, tile_dic: Dict[Coordinate, Tile] = None):
        super().__init__(AreaType.BossRoom, hallway, direction, boss, tile_dic)

    def abbreviation(self) -> str:
        return "BR"


class Placeholder:
    class _AreaPlaceholder(Area):
        def __init__(self, code: int):
            if code == 0:
                # horizontal Hallway
                self.__has_full_row = True
            elif code == 1:
                # vertical Hallway
                self.__has_full_row = False
            else:
                # room
                self.__has_full_row = True
            super().__init__(AreaType.Placeholder, [[Area.void()]])

        def at(self, x: int, y: int, force: bool = False) -> Tile:
            return Area.void()

        def get_row_str(self, row: int) -> str:
            void_str = Area.void().get_img()
            if self.__has_full_row:
                return void_str * Area.UNIT_WIDTH
            else:
                return void_str

        def in_sight(self):
            pass

        def enter(self, direction: Direction):
            pass

    class _RoomPlaceHolder(Room):
        def __init__(self):
            super(Placeholder._RoomPlaceHolder, self).__init__(AreaType.Invalid, [])

        def abbreviation(self) -> str:
            return "PH"

        def at(self, x: int, y: int, force: bool = False, inside_only: bool = False) -> Tile:
            return Invalid()

    __HORIZONTAL = _AreaPlaceholder(0)
    __VERTICAL = _AreaPlaceholder(1)
    __ROOM = _AreaPlaceholder(2)

    @staticmethod
    def horizontal() -> _AreaPlaceholder:
        return Placeholder.__HORIZONTAL

    @staticmethod
    def vertical() -> _AreaPlaceholder:
        return Placeholder.__VERTICAL

    @staticmethod
    def pseudo_room() -> _AreaPlaceholder:
        return Placeholder.__ROOM

    @staticmethod
    def empty_room(hw_dic: Dict[Direction, "Hallway"]) -> "CopyAbleRoom":
        return EmptyRoom(hw_dic)

    @staticmethod
    def room() -> _RoomPlaceHolder:
        return Placeholder._RoomPlaceHolder()
