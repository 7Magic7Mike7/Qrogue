from abc import ABC, abstractmethod
from typing import List, Callable

from qrogue.game.map import tiles
from qrogue.game.actors.controllable import Controllable
from qrogue.game.map.navigation import Coordinate, Direction
from qrogue.game.map.rooms import Room, Area, Placeholder, SpawnRoom, MetaRoom
from qrogue.game.save_data import SaveData
from qrogue.util.config import Config
from qrogue.util.logger import Logger
from qrogue.widgets.my_popups import CommonQuestions


class Map(ABC):
    DONE_EVENT_ID = "Done".lower()

    @staticmethod
    def __calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate) -> Coordinate:
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

    def __init__(self, name: str, seed: int, rooms: List[List[Room]], controllable: Controllable,
                 spawn_room: Coordinate, proceed_to_next_map: Callable[[], None]):
        self.__name = name
        self.__seed = seed
        self.__rooms = rooms
        self.__controllable_tile = tiles.ControllableTile(controllable)
        self.__proceed_to_next_map = proceed_to_next_map

        self.__dimensions = Coordinate(len(rooms[0]), len(rooms))

        self.__controllable_pos = Map.__calculate_pos(spawn_room, Coordinate(Area.MID_X, Area.MID_Y))
        self.__cur_area = self.__rooms[spawn_room.y][spawn_room.x]
        self.__cur_area.enter(Direction.Center)
        self.__cur_area.make_visible()

        if isinstance(self.__cur_area, SpawnRoom):
            self.__cur_area.set_is_done_callback(self.__is_done)
        elif not isinstance(self.__cur_area, MetaRoom):
            Logger.instance().error(f"{name} starts in area that is not a SpawnRoom! cur_area = {self.__cur_area}")

    @property
    def name(self) -> str:
        return self.__name

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
        return self.width * (Area.UNIT_WIDTH + 1) - 1

    @property
    def full_height(self) -> int:
        return self.height * (Area.UNIT_HEIGHT + 1) - 1

    @property
    def controllable_tile(self) -> tiles.ControllableTile:
        return self.__controllable_tile

    @property
    def controllable_pos(self) -> Coordinate:
        return self.__controllable_pos

    @abstractmethod
    def is_world(self) -> bool:
        pass

    def __proceed(self, confirmed: bool = True):
        if confirmed and self.__proceed_to_next_map:
            self.__proceed_to_next_map()

    def __get_area(self, x: int, y: int) -> (Area, tiles.Tile):
        """
        Calculates and returns the Room and in-room Coordinates of the given Map position.
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
                Logger.instance().error(f"Error! You should not be able to move outside of Hallways: {x}|{y}")
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
            Logger.instance().error(f"Error! Invalid position: {x}|{y}")
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

    def room_at(self, x: int, y: int) -> Room:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.__rooms[y][x]
        return None

    def move(self, direction: Direction) -> bool:
        """
        Tries to move the robot into the given Direction.
        :param direction: in which direction the robot should move
        :return: True if the robot was able to move, False otherwise
        """
        new_pos = self.__controllable_pos + direction
        if new_pos.y < 0 or self.full_height <= new_pos.y or \
                new_pos.x < 0 or self.full_width <= new_pos.x:
            return False

        area, tile = self.__get_area(new_pos.x, new_pos.y)
        if tile.is_walkable(direction, self.__controllable_tile.controllable):
            if area != self.__cur_area:
                self.__cur_area.leave(direction)
                self.__cur_area = area
                self.__cur_area.enter(direction)

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.trigger(direction, self.controllable_tile.controllable, self.__trigger_event)

            self.__controllable_pos = new_pos
            return True
        else:
            return False

    def __is_done(self) -> bool:
        return SaveData.instance().achievement_manager.check_achievement(self.DONE_EVENT_ID)

    def __trigger_event(self, event_id: str):
        if event_id.lower() == self.DONE_EVENT_ID:
            if self.is_world():
                SaveData.instance().achievement_manager.finished_world(self.name)
            else:
                SaveData.instance().achievement_manager.finished_level(self.name)  # todo what about expeditions?
            CommonQuestions.ProceedToNextMap.ask(self.__proceed)
        SaveData.instance().achievement_manager.trigger_level_event(event_id)
        if Config.debugging():
            print("triggered event: " + event_id)

    def row_strings(self) -> List[str]:
        rows = []
        offset = 0
        # iterate through every row of Rooms
        for y in range(self.height):
            last_row = y == self.height - 1  # there are no more Hallways after the last row of Rooms
            areas = []
            south_hallways = []

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
