
from abc import ABC, abstractmethod
from enum import Enum

import py_cui

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.navigation import Direction


class TileCode(Enum):
    Invalid = -1    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Debug = -2      # displays a digit for debugging
    Void = 7        # tile outside of the playable area
    Floor = 0       # simple floor tile without special meaning
    HallwayEntrance = 5     # depending on the hallway it refers to is either a Floor or Wall
    FogOfWar = 3    # tile of a place we cannot see yet

    Message = 6         # tile for displaying a popup message
    Trigger = 9         # tile that calls a function on walk, i.e. event tile
    Teleport = 91       # special trigger for teleporting between maps
    Decoration = 11     # simply displays a specified character

    Wall = 1
    Obstacle = 2
    Door = 4

    Controllable = 20
    Enemy = 30
    Boss = 40

    Collectible = 50
    Riddler = 51
    ShopKeeper = 52
    Energy = 53

    SpaceshipBlock = 70
    SpaceshipWalk = 71
    SpaceshipTrigger = 72
    OuterSpace = 73


class TileColorer:
    __color_manager = {
        TileCode.Invalid: py_cui.RED_ON_BLUE,
        TileCode.Void: py_cui.CYAN_ON_BLACK,
        TileCode.Floor: py_cui.CYAN_ON_BLACK,
        TileCode.Wall: py_cui.BLACK_ON_WHITE,
        TileCode.Obstacle: py_cui.CYAN_ON_BLACK,
        TileCode.FogOfWar: py_cui.CYAN_ON_BLACK,
        TileCode.Door: py_cui.CYAN_ON_BLACK,
        TileCode.Collectible: py_cui.CYAN_ON_BLACK,
        TileCode.Controllable: py_cui.GREEN_ON_BLACK,
        TileCode.Enemy: py_cui.RED_ON_BLACK,
        TileCode.Boss: py_cui.BLACK_ON_RED,
        TileCode.SpaceshipWalk: py_cui.BLACK_ON_WHITE,
    }

    @staticmethod
    def get_color(tile_code: TileCode) -> int:
        """

        :param tile_code: code of the Tile we want to get the default color of
        :return: integer representing one of the possible foreground-background color comibnations, None for invalid
        input
        """
        if tile_code in TileColorer.__color_manager:
            return TileColorer.__color_manager[tile_code]


class Tile(ABC):
    @staticmethod
    def _invisible_tile():
        return " "

    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def code(self) -> TileCode:
        return self.__code

    @property
    def _invisible(self):
        return Tile._invisible_tile()

    @abstractmethod
    def get_img(self):
        pass

    @abstractmethod
    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        pass

    @abstractmethod
    def copy(self) -> "Tile":
        pass

    def __str__(self):
        return self.get_img()


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Invalid()


class Debug(Tile):
    def __init__(self, num: int):
        super(Debug, self).__init__(TileCode.Debug)
        self.__num = str(num)[0]

    def get_img(self) -> str:
        return self.__num

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Debug(int(self.__num))


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Void()


class Floor(Tile):
    @staticmethod
    def img():
        return Tile._invisible_tile()

    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return Floor.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def copy(self) -> "Tile":
        return Floor()


class Wall(Tile):
    @staticmethod
    def img():
        return "#"

    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return Wall.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Wall()


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Obstacle()


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def copy(self) -> "Tile":
        return FogOfWar()


class Decoration(Tile):
    def __init__(self, decoration: str, blocking: bool = False):
        super(Decoration, self).__init__(TileCode.Decoration)
        self.__decoration = decoration
        self.__blocking = blocking

    def get_img(self):
        return self.__decoration

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return not self.__blocking

    def copy(self) -> "Tile":
        return Decoration(self.__decoration, self.__blocking)


class ControllableTile(Tile):
    def __init__(self, controllable: Controllable):
        super().__init__(TileCode.Controllable)
        self.__controllable = controllable

    def get_img(self):
        return self.__controllable.get_img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True # todo check

    @property
    def controllable(self) -> Controllable:
        return self.__controllable

    def copy(self) -> "Tile":
        return ControllableTile(self.__controllable)
