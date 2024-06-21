from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from qrogue.game.logic.collectibles import CollectibleType
from qrogue.game.world import tiles
from qrogue.game.world.map import rooms, LevelMap
from qrogue.game.world.navigation import Coordinate
from qrogue.util import Logger
from qrogue.util.util_functions import my_str, enum_from_str


class WFCLearnMatrix(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @property
    @abstractmethod
    def type(self) -> Any:
        pass

    @abstractmethod
    def at(self, x: int, y: int) -> Any:
        """

        :param x:
        :param y:
        :return: a value of the feature we want to learn about
        """
        pass


class LearnableMap(WFCLearnMatrix):
    def __init__(self, level_map: LevelMap):
        self.__level_map = level_map

    @property
    def width(self) -> int:
        return self.__level_map.width

    @property
    def height(self) -> int:
        return self.__level_map.height

    @property
    def type(self) -> Any:
        return rooms.AreaType

    def at(self, x: int, y: int) -> rooms.AreaType:
        room = self.__level_map.room_at(x, y)
        if room is None:
            return rooms.AreaType.Invalid
        return room.type


class LearnableRoom(WFCLearnMatrix):
    class TileData:
        __DATA_PREFIX = " ("
        __DATA_SUFFIX = ")"

        @staticmethod
        def from_string(tile_data: str) -> Optional["LearnableRoom.TileData"]:
            # retrieve data if present
            prefix = LearnableRoom.TileData.__DATA_PREFIX
            if prefix in tile_data:
                data_start = tile_data.index(prefix) + len(prefix)
                data_end = tile_data.index(LearnableRoom.TileData.__DATA_SUFFIX, data_start)
                data = tile_data[data_start:data_end]
                tile_data = tile_data[:data_start-len(prefix)]  # don't include prefix
            else:
                data = None

            # parse TileCode
            tile_code = enum_from_str(tiles.TileCode, tile_data)
            if tile_code is tiles.TileCode.Enemy:
                if data is None:
                    Logger.instance().warn(f"Tried to create TileData for Enemy without specified data: {tile_data}",
                                           from_pycui=False)
                    return None
                data = int(data)    # enemies use their id as data

            elif tile_code is tiles.TileCode.Collectible:
                if data is None:
                    Logger.instance().warn(f"Tried to create TileData for unspecified Collectible without data: "
                                           f"{tile_data}", from_pycui=False)
                    return None
                data = enum_from_str(CollectibleType, data)

            return LearnableRoom.TileData(tile_code, data)

        def __init__(self, code: tiles.TileCode, data: Any):
            self.__code = code
            self.__data = data

            if data is not None and not isinstance(data, int) and not isinstance(data, CollectibleType):
                from qrogue.util import Config
                Config.check_reachability(f"unexpected type for data: {data}")

        @property
        def code(self) -> tiles.TileCode:
            return self.__code

        @property
        def data(self) -> Any:
            return self.__data

        def __hash__(self):
            if self.__data is None:
                return hash(self.__code)
            else:
                return hash(self.__code) * 17 + hash(self.__data)

        def __eq__(self, other):
            if isinstance(other, tiles.TileCode):
                return other == self.__code
            elif isinstance(other, LearnableRoom.TileData):
                return other.__code == self.__code and other.__data == self.__data
            else:
                return False

        def __str__(self):
            return f"{self.__code.name}" + \
                ("" if self.__data is None else
                 f"{LearnableRoom.TileData.__DATA_PREFIX}{my_str(self.__data)}{LearnableRoom.TileData.__DATA_SUFFIX}")

    def __init__(self, room: rooms.Room):
        self.__room = room

    @property
    def width(self) -> int:
        return rooms.Room.INNER_WIDTH

    @property
    def height(self) -> int:
        return rooms.Room.INNER_HEIGHT

    @property
    def type(self) -> Any:
        return tiles.TileCode

    def at(self, x: int, y: int) -> TileData:
        tile = self.__room.at(x, y, force=True, inside_only=True)
        return LearnableRoom.TileData(tile.code, tile.data)


class LearnableRoomMatrix(WFCLearnMatrix):
    def __init__(self, room_dict: Dict[Coordinate, LearnableRoom.TileData]):
        self.__matrix = room_dict
        self.__width = 0
        self.__height = 0

        for coor in room_dict.keys():
            if coor.x > self.__width:
                self.__width = coor.x
            if coor.y > self.__height:
                self.__height = coor.y

        # increment width and height since coordinates start at 0
        self.__width += 1
        self.__height += 1

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def type(self) -> Any:
        return tiles.TileCode

    def at(self, x: int, y: int) -> LearnableRoom.TileData:
        coor = Coordinate(x, y)
        if coor in self.__matrix:
            return self.__matrix[Coordinate(x, y)]
        else:
            return LearnableRoom.TileData(tiles.TileCode.Invalid, None)
