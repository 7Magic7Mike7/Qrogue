
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.navigation import Direction
from qrogue.util import CheatConfig


class TileCode(Enum):
    Invalid = (-1, "§")    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Debug = (-2, "€")      # displays a digit for debugging
    Void = (7, "_")        # tile outside the playable area
    Floor = (0, " ")       # simple floor tile without special meaning
    HallwayEntrance = (5, " ")     # depending on the hallway it refers to is either a Floor or Wall
    FogOfWar = (3, "~")    # tile of a place we cannot see yet

    Message = (6, ".")         # tile for displaying a popup message
    Goal = (61, "G")            # tile for the goal, i.e. end of a level
    Trigger = (9, "T")         # tile that calls a function on walk, i.e. event tile
    Teleport = (91, "t")       # special trigger for teleporting between maps
    Decoration = (11, "d")     # simply displays a specified character

    Wall = (1, "#")
    Obstacle = (2, "o")
    Door = (4, "|")

    Controllable = (20, "C")
    # Npc = (25, "N")
    Enemy = (30, "E")
    Boss = (40, "B")

    Collectible = (50, "c")
    Riddler = (51, "?")
    # ShopKeeper = (52, "$")
    Energy = (53, "e")
    Challenger = (54, "!")

    # SpaceshipBlock = (70, "/")
    # SpaceshipWalk = (71, ".")
    # SpaceshipTrigger = (72, "T")
    # OuterSpace = (73, "*")

    CollectibleKey = (501, "k")
    # CollectibleCoin = (502, "€")
    CollectibleEnergy = (503, "e")
    CollectibleScore = (504, "s")
    CollectibleGate = (520, "g")
    CollectibleQubit = (560, "q")

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

    @staticmethod
    def special_values() -> List["TileCode"]:
        return [
            TileCode.Invalid, TileCode.Debug, TileCode.Void, TileCode.FogOfWar,
            TileCode.Message, TileCode.Trigger, TileCode.Teleport, TileCode.Decoration,
        ]

    @staticmethod
    def collectible_subtypes() -> List["TileCode"]:
        return [
            TileCode.Collectible,
            TileCode.CollectibleKey, TileCode.CollectibleEnergy,
            TileCode.CollectibleGate, TileCode.CollectibleQubit,
            TileCode.CollectibleScore,
        ]


class Tile(ABC):
    @staticmethod
    def _invisible_tile():
        return " "

    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def data(self) -> None:
        """
        E.g. amount for Energy, logical Collectible for Collectibles, eid for Enemies or None for tiles without any
        dynamic values (Walls, Floor, ...)

        :return: a representation of the specific tile's data
        """
        return None

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

    @property
    def data(self) -> None:
        return None

    def get_img(self):
        return TileCode.Invalid.representation

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Invalid()


class Debug(Tile):
    def __init__(self, num: int):
        super(Debug, self).__init__(TileCode.Debug)
        self.__num = str(num)[0]

    @property
    def data(self) -> int:
        return int(self.__num)

    def get_img(self) -> str:
        return self.__num

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Debug(int(self.__num))


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    @property
    def data(self) -> None:
        return None

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

    @property
    def data(self) -> None:
        return None

    def get_img(self):
        return Floor.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def copy(self) -> "Tile":
        return Floor()


class Wall(Tile):
    @staticmethod
    def img():
        return TileCode.Wall.representation

    def __init__(self):
        super().__init__(TileCode.Wall)

    @property
    def data(self) -> None:
        return None

    def get_img(self):
        return Wall.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False

    def copy(self) -> "Tile":
        return Wall()


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    @property
    def data(self) -> None:
        return None

    def get_img(self):
        return TileCode.Obstacle.representation

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False or CheatConfig.ignore_obstacles()

    def copy(self) -> "Tile":
        return Obstacle()


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    @property
    def data(self) -> None:
        return None

    def get_img(self):
        return TileCode.FogOfWar.representation

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def copy(self) -> "Tile":
        return FogOfWar()


class Decoration(Tile):
    def __init__(self, decoration: str, blocking: bool = False):
        super(Decoration, self).__init__(TileCode.Decoration)
        self.__decoration = decoration
        self.__blocking = blocking

    @property
    def data(self) -> bool:
        return self.__blocking

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

    @property
    def data(self) -> str:
        return self.__controllable.name

    def get_img(self):
        return self.__controllable.get_img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True # todo check

    @property
    def controllable(self) -> Controllable:
        return self.__controllable

    def copy(self) -> "Tile":
        return ControllableTile(self.__controllable)
