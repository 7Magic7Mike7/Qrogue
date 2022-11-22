
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.navigation import Direction
from qrogue.util import CheatConfig


class TileCode(Enum):
    Invalid = (-1, "§")    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Debug = (-2, "€")      # displays a digit for debugging
    Void = (7, "_")        # tile outside of the playable area
    Floor = (0, " ")       # simple floor tile without special meaning
    HallwayEntrance = (5, " ")     # depending on the hallway it refers to is either a Floor or Wall
    FogOfWar = (3, "~")    # tile of a place we cannot see yet

    Message = (6, ".")         # tile for displaying a popup message
    Trigger = (9, "T")         # tile that calls a function on walk, i.e. event tile
    Teleport = (91, "t")       # special trigger for teleporting between maps
    Decoration = (11, "d")     # simply displays a specified character

    Wall = (1, "#")
    Obstacle = (2, "o")
    Door = (4, "|")

    Controllable = (20, "C")
    Npc = (25, "N")
    Enemy = (30, "E")
    Boss = (40, "B")

    Collectible = (50, "c")
    Riddler = (51, "?")
    ShopKeeper = (52, "$")
    Energy = (53, "e")
    Challenger = (54, "!")

    SpaceshipBlock = (70, "/")
    SpaceshipWalk = (71, ".")
    SpaceshipTrigger = (72, "T")
    OuterSpace = (73, "*")

    def __init__(self, id: int, representation: str):
        self.__id = id
        self.__representation = representation

    @property
    def id(self) -> int:
        return self.__id

    @property
    def representation(self) -> str:
        return self.__representation

    def __str__(self):
        return self.representation


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
        return False or CheatConfig.ignore_obstacles()

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


class NpcTile(Tile):
    def __init__(self, name: str, show_message_callback: Callable[[str, str], None],
                 get_text_callback: Callable[[], str]):
        super(NpcTile, self).__init__(TileCode.Npc)
        self.__name = name
        self.__show_message = show_message_callback
        self.__get_text = get_text_callback

    def get_img(self):
        return self.__name[0]

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        self.__show_message(self.__name, self.__get_text())
        return False

    def copy(self) -> "Tile":
        return NpcTile(self.__name, self.__show_message, self.__get_text)
