from typing import List

import game.map.tiles as tiles
from game.actors.robot import Robot
from game.callbacks import CallbackPack
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, Area
from util.config import Config
from util.logger import Logger


class Map:
    MAX_WIDTH = 7
    MAX_HEIGHT = 3

    @staticmethod
    def __calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate) -> Coordinate:
        """
        Calculates and returns a Coordinate on the Map corresponding to the Cooridante of a Room on the Map and
        a Coordinate in the Room.

        :param pos_of_room: Coordinate of the Room on the Map
        :param pos_in_room: Coordinate in the Room
        :return: Coordinate on the Map
        """
        x = pos_of_room.x * (Area.UNIT_WIDTH + 1) + pos_in_room.x
        y = pos_of_room.y * (Area.UNIT_HEIGHT + 1) + pos_in_room.y
        return Coordinate(x, y)

    def __init__(self, seed: int, rooms: List[List[Room]], robot: Robot, spawn_room: Coordinate, cbp: CallbackPack):
        self.__seed = seed
        self.__rooms = rooms
        self.__robot = tiles.RobotTile(robot)
        self.__cbp = cbp

        self.__dimensions = Coordinate(len(rooms[0]), len(rooms))

        self.__robot_pos = Map.__calculate_pos(spawn_room, Coordinate(Area.MID_X, Area.MID_Y))
        self.__cur_area = self.__rooms[spawn_room.y][spawn_room.x]
        self.__cur_area.enter(Direction.Center)
        self.__cur_area.make_visible()

        # todo better solution would be nice, but since our sizes are fixed it doesn't make sense performance-wise
        # e.g. maximal WIDTH * HEIGHT * 4 = 7 * 3 * 4 = 84 iterations
        # set the check event callback for all doors
        for room_row in rooms:
            for room in room_row:
                if room:
                    for direction in Direction.values():
                        hw = room.get_hallway(direction, throw_error=False)
                        if hw:
                            hw.set_check_event_callback(self.check_event)

        self.__events = {}

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
    def robot_tile(self) -> tiles.RobotTile:
        return self.__robot

    @property
    def robot_pos(self) -> Coordinate:
        return self.__robot_pos

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
        new_pos = self.__robot_pos + direction
        if new_pos.y < 0 or self.full_height <= new_pos.y or \
                new_pos.x < 0 or self.full_width <= new_pos.x:
            return False

        area, tile = self.__get_area(new_pos.x, new_pos.y)
        if tile.is_walkable(direction, self.__robot.robot):
            if area != self.__cur_area:
                self.__cur_area.leave(direction)
                self.__cur_area = area
                self.__cur_area.enter(direction)

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.trigger(direction, self.robot_tile.robot, self.__trigger_event)

            self.__robot_pos = new_pos
            return True
        else:
            return False

    def check_event(self, event_id: str) -> bool:
        return event_id in self.__events

    def __trigger_event(self, event_id: str):
        if Config.debugging():
            print("triggered event: " + event_id)
        self.__events[event_id] = True

