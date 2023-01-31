from abc import ABC, abstractmethod
from typing import Any

from qrogue.game.world import tiles
from qrogue.game.world.map import rooms, LevelMap


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
        def __init__(self, code: tiles.TileCode, data: Any):
            self.__code = code
            self.__data = data

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
