import enum
from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Tuple

import qrogue.game.world.tiles as tiles
from qrogue.game.logic import Message
from qrogue.game.logic.actors import Controllable, Robot
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import Logger, MapConfig

from qrogue.game.world.map.rooms import Room, Area, Placeholder, SpawnRoom, MetaRoom, AreaType


class MapType(enum.Enum):
    World = 0
    Level = 1
    Expedition = 2


class MapMetaData:
    def __init__(self, name: Optional[str], description: Optional[Message], has_teleporter: bool,
                 show_description: Callable[[], None], show_individual_qubits: bool = False):
        self.name = name
        self.description = description
        self.has_teleporter = has_teleporter
        self.__show_description = show_description
        self.show_individual_qubits = show_individual_qubits

    def show_description(self):
        self.__show_description()


class BaseMap(ABC):
    @staticmethod
    def _calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate) -> Coordinate:
        """
        Calculates and returns a Coordinate on the Map corresponding to the Coordinate of a Room on the Map and
        a Coordinate in the Room.

        :param pos_of_room: Coordinate of the Room on the Map
        :param pos_in_room: Coordinate in the Room
        :return: Coordinate on the Map
        """
        x = pos_of_room.x * (Area.UNIT_WIDTH + 1) + pos_in_room.x
        y = pos_of_room.y * (Area.UNIT_HEIGHT + 1) + pos_in_room.y
        return Coordinate(x, y)

    def __init__(self, meta_data: MapMetaData, internal_name: str, seed: int, rooms: List[List[Optional[Room]]]):
        self.__meta_data = meta_data
        self.__internal_name = internal_name
        self.__seed = seed
        self.__rooms = rooms
        self.__dimensions = Coordinate(len(rooms[0]), len(rooms))

    @property
    def _meta_data(self) -> MapMetaData:
        return self.__meta_data

    @property
    def _rooms(self) -> List[List[Optional[Room]]]:
        return self.__rooms

    @property
    def name(self) -> str:
        """
        Name of the Map that is presented to the player.
        Can be the same as its internal name.
        :return: name of the Map that is shown in-game
        """
        if self.__meta_data.name is None:  # show the internal name if no display name was specified
            return self.__internal_name
        return self.__meta_data.name

    @property
    def internal_name(self) -> str:
        """
        Name of the Map that is used to identify it in the game's logic (e.g. for events).
        :return: name of the Map that is used internally
        """
        return self.__internal_name

    @property
    def seed(self) -> int:
        return self.__seed

    @property
    def width(self) -> int:
        return self.__dimensions.x

    @property
    def height(self) -> int:
        return self.__dimensions.y

    @property
    def full_width(self) -> int:
        """

        :return:
        """
        return self.width * (Area.UNIT_WIDTH + 1) - 1

    @property
    def full_height(self) -> int:
        return self.height * (Area.UNIT_HEIGHT + 1) - 1

    @abstractmethod
    def get_type(self) -> MapType:
        pass

    def _get_area(self, x: int, y: int) -> Tuple[Optional[Area], tiles.Tile]:
        """
        Calculates and returns the Room and in-room Coordinates of the given Map position (globally, not room position!).
        :param x: x position on the Map
        :param y: y position on the Map
        :return: Room or Hallway and their Tile at the given position
        """
        in_hallway = None
        width = Area.UNIT_WIDTH + 1
        height = Area.UNIT_HEIGHT + 1
        x_mod = x % width
        y_mod = y % height
        # position is in Hallway
        if x_mod == Area.UNIT_WIDTH:
            if y_mod == Area.UNIT_HEIGHT:
                # there are a few points on the map that are surrounded by Hallways and don't belong to any Room
                Logger.instance().error(f"Error! You should not be able to move outside of Hallways: {x}|{y}",
                                        from_pycui=False)
                return None, tiles.Invalid()
            x -= 1
            x_mod -= 1
            in_hallway = Direction.East
        elif y_mod == Area.UNIT_HEIGHT:
            y -= 1
            y_mod -= 1
            in_hallway = Direction.South

        room_x = int(x / width)
        room_y = int(y / height)
        room = self.__rooms[room_y][room_x]
        if room is None:
            Logger.instance().error(f"Error! Invalid position: {x}|{y}", from_pycui=False)
            return None, tiles.Invalid()

        if in_hallway:
            hallway = room.get_hallway(in_hallway)
            if hallway is None:
                return None, tiles.Invalid()
            if hallway.is_horizontal():
                return hallway, hallway.at(x_mod, 0)
            else:
                return hallway, hallway.at(0, y_mod)
        else:
            return room, room.at(x_mod, y_mod)

    def room_at(self, x: int, y: int) -> Optional[Room]:
        """
        Returns the Room at the given position or None if either x or y are out of bounds.

        :param x: x-Coordinate of the room we want to get
        :param y: y-Coordinate of the room we want to get
        :return: the Room at the given position or None if the position is invalid
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.__rooms[y][x]
        return None

    def row_strings(self) -> List[str]:
        rows: List[str] = []
        offset = 0
        # iterate through every row of Rooms
        for y in range(self.height):
            last_row = y == self.height - 1  # there are no more Hallways after the last row of Rooms
            areas: List[Area] = []
            south_hallways: List[str] = []

            for x in range(self.width):
                last_col = x == self.width - 1  # there are no more Hallways after the last Room in a row
                room = self.room_at(x, y)
                if room is None:
                    areas.append(Placeholder.pseudo_room())
                    if not last_col:
                        areas.append(Placeholder.vertical())
                    if not last_row:
                        south_hallways.append(Placeholder.horizontal().get_row_str(0))

                else:
                    areas.append(room)
                    if not last_col:
                        hallway = room.get_hallway(Direction.East, throw_error=False)
                        if hallway is None:
                            areas.append(Placeholder.vertical())
                        else:
                            areas.append(hallway)
                    if not last_row:
                        hallway = room.get_hallway(Direction.South, throw_error=False)
                        if hallway is None:
                            south_hallways.append(Placeholder.horizontal().get_row_str(0))
                        else:
                            south_hallways.append(hallway.get_row_str(0))

            rows += ([""] * Area.UNIT_HEIGHT)  # initialize the new "block" of rows with empty strings
            for area in areas:
                for ry in range(Area.UNIT_HEIGHT):
                    rows[offset + ry] += area.get_row_str(ry)
            rows.append(Area.void().get_img().join(south_hallways))
            offset += Area.UNIT_HEIGHT + 1
        return rows

    def __str__(self):
        return "\n".join(self.row_strings())


class Map(BaseMap, ABC):
    def __init__(self, meta_data: MapMetaData, internal_name: str, seed: int, rooms: List[List[Optional[Room]]],
                 controllable: Controllable, spawn_room: Coordinate, check_achievement: Callable[[str], bool],
                 trigger_event: Callable[[str], None]):
        super().__init__(meta_data, internal_name, seed, rooms)
        self.__check_achievement = check_achievement
        self.__trigger_event = trigger_event

        self.__controllable_tile = tiles.ControllableTile(controllable)
        self.__controllable_pos = BaseMap._calculate_pos(spawn_room, Coordinate(Area.MID_X, Area.MID_Y))
        self.__move_direction = Direction.Center    # initially we didn't move in any direction

        self.__cur_area = self.room_at(spawn_room.x, spawn_room.y)
        if self.__cur_area is None:
            Logger.instance().error(f"Illegal spawn room @{spawn_room} for map {meta_data.name}")
        else:
            self.__cur_area.enter(Direction.Center)
            self.__cur_area.make_visible()

            if isinstance(self.__cur_area, SpawnRoom):
                self.__cur_area.set_is_done_callback(self._is_done)
            elif not isinstance(self.__cur_area, MetaRoom) and self.__cur_area.type is not AreaType.SpawnRoom:
                Logger.instance().error(f"{meta_data.name} starts in area that is not a SpawnRoom! cur_area = "
                                        f"{self.__cur_area}", from_pycui=False)

    @property
    def controllable_tile(self) -> tiles.ControllableTile:
        return self.__controllable_tile

    @property
    def controllable_pos(self) -> Coordinate:
        return self.__controllable_pos

    @property
    def show_individual_qubits(self) -> bool:
        return self._meta_data.show_individual_qubits

    def _is_done(self) -> bool:
        return self.__check_achievement(MapConfig.done_event_id())

    def start(self):
        self._meta_data.show_description()

    def move(self, direction: Direction) -> bool:
        """
        Tries to move the robot into the given Direction.
        :param direction: in which direction the robot should move
        :return: True if the robot was able to move, False otherwise
        """
        if self.controllable_tile.controllable.game_over_check():
            # although moving does not cost energy, this can still be True if we didn't get back energy after a puzzle
            # todo fix somehow since it is awkward to immediately lose after solving a puzzle correctly
            return False

        new_pos = self.__controllable_pos + direction
        if new_pos.y < 0 or self.full_height <= new_pos.y or \
                new_pos.x < 0 or self.full_width <= new_pos.x:
            return False

        area, tile = self._get_area(new_pos.x, new_pos.y)
        if tile.is_walkable(direction, self.controllable_tile.controllable):
            robot = self.controllable_tile.controllable
            if isinstance(robot, Robot):
                robot.on_move()

            if area != self.__cur_area:
                self.__cur_area.leave(direction)
                self.__cur_area = area
                self.__cur_area.enter(direction)

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.trigger(direction, self.controllable_tile.controllable, self.__trigger_event)

            self.__controllable_pos = new_pos
            self.__move_direction = direction
            return True
        else:
            return False

    def undo_last_move(self) -> bool:
        """
        Tries to undo the last movement (i.e., move in the opposite direction). Fails at the beginning of a Map when
        there was no movement yet or if something blocks the Controllable to move back (e.g., directional doors).

        :return: True if we were able to undo the last move, False otherwise
        """
        if self.__move_direction is Direction.Center: return False

        return self.move(self.__move_direction.opposite())

    def tunnel(self, pos_of_room: Coordinate, pos_in_room: Optional[Coordinate]) -> bool:
        if pos_in_room is None:
            _x, _y = MapConfig.room_mid()
            pos_in_room = Coordinate(_x, _y)

        room = self.room_at(pos_of_room.x, pos_of_room.y)
        if room is None:
            return False

        target_pos = BaseMap._calculate_pos(pos_of_room, pos_in_room)
        direction = Direction.from_coordinates(self.__controllable_pos, target_pos)
        destination_tile = room.at(pos_in_room.x, pos_in_room.y, force=True)
        if destination_tile.is_walkable(direction, self.controllable_tile.controllable):
            self.__controllable_pos = target_pos
            return True
        return False

    def __str__(self):
        return "\n".join(self.row_strings())
