from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Tuple

from qrogue.game.world.dungeon_generator import QrogueLevelGenerator
from qrogue.game.world.dungeon_generator.dungeon_parser.QrogueDungeonParser import QrogueDungeonParser
from qrogue.game.world.map import rooms, LevelMap
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import tiles


class WFCLearner:
    class WFCLearnMatrix(ABC):
        @property
        @abstractmethod
        def width(self) -> int:
            pass

        @property
        @abstractmethod
        def height(self) -> int:
            pass

        @abstractmethod
        def at(self, x: int, y: int) -> Any:
            pass

    def __init__(self, pos_weights: Dict[Coordinate, Dict[Any, int]],
                 type_weights: Dict[Optional[Any], Dict[Any, int]]):
        pass

    def learn(self, matrix: WFCLearnMatrix):
        pass


# todo subclassing QrogueLevelGenerator seems inefficient due to handling rooms and other stuff we don't need
class WFCLayoutLearner(QrogueLevelGenerator):
    def __init__(self, pos_weights: Dict[Coordinate, Dict[rooms.AreaType, int]],
                 type_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]],
                 connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]]):
        def trigger_event(_: str):
            pass

        def load_map_callback(_: str, __: Coordinate):
            pass

        def show_message_callback(_: str, __: str, ___: Optional[bool], ____: Optional[int]):
            pass
        # seed is not needed since we don't work with room content
        super().__init__(0, lambda _: False, trigger_event, load_map_callback, show_message_callback)

        self.__pos_weights: Dict[Coordinate, Dict[rooms.AreaType, int]] = pos_weights
        self.__type_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = type_weights
        self.__connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = \
            connection_weights

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[Optional[LevelMap], bool]:
        _, success = super(WFCLayoutLearner, self).generate(file_name, in_dungeon_folder)
        return None, success

    def visitLayout(self, ctx: QrogueDungeonParser.LayoutContext) -> List[List[rooms.Room]]:
        room_matrix = super(WFCLayoutLearner, self).visitLayout(ctx)

        def get_room_type(x_: int, y_: int) -> rooms.AreaType:
            if 0 <= y_ < len(room_matrix) and 0 <= x_ < len(room_matrix[y_]):
                if room_matrix[y_][x_] is None:
                    return rooms.AreaType.EmptyRoom
                else:
                    return room_matrix[y_][x_].type
            else:
                return rooms.AreaType.Invalid

        for y in range(len(room_matrix)):
            for x in range(len(room_matrix[y])):
                room = room_matrix[y][x]
                if room is None:
                    rtype = rooms.AreaType.EmptyRoom
                else:
                    rtype = room.type

                # init dicts if needed
                c = Coordinate(x, y)
                if c not in self.__pos_weights:
                    self.__pos_weights[c] = {}
                if rtype not in self.__type_weights:
                    self.__type_weights[rtype] = {}
                    self.__connection_weights[rtype] = {}
                cur_dict = self.__type_weights[rtype]

                # increase weight of this room's type for the current position
                if rtype in self.__pos_weights[c]:
                    self.__pos_weights[c][rtype] += 1
                else:
                    self.__pos_weights[c][rtype] = 1

                # find out the type of the room's neighbors
                neighbors: Dict[Direction, rooms.AreaType] = {}
                for val in Direction.values():
                    neighbors[val] = get_room_type(x + val.x, y + val.y)

                # update the weights accordingly
                for direction in neighbors:
                    ntype = neighbors[direction]
                    if ntype in cur_dict:
                        cur_dict[ntype] += 1
                    else:
                        cur_dict[ntype] = 1

                    # check for hallway
                    if room is not None and room.get_hallway(direction, throw_error=False) is not None:
                        if ntype in self.__connection_weights[rtype]:
                            self.__connection_weights[rtype][ntype] += 1
                        else:
                            self.__connection_weights[rtype][ntype] = 1

        return room_matrix
