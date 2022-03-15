import random
from typing import Callable, List

from qrogue.game.logic.actors import Robot, Controllable, Player
from qrogue.game.world.navigation import Direction, Coordinate
from qrogue.game.world.tiles import Tile, TileCode, WalkTriggerTile
from qrogue.util import MyRandom

ascii_spaceship = \
    r"                                                                                              " + "\n" \
    r"                                    X---------------X                                         " + "\n" \
    r"                                   /ööööööööööööööööö)>                                       " + "\n" \
    r"                                  /öööööööööööööööööö)>                           /)          " + "\n" \
    r"                                 /ööööööööööööööööööö)>                          /ö|          " + "\n" \
    r"                                |öööööööööööööööööööö)>                         /öö|          " + "\n" \
    r"                                |öööööööööööööööööööö)>                        /ööö|          " + "\n" \
    r"                                |ööööööööööööööööööö/                         /öööö|          " + "\n" \
    r"                               /ööööööööööööööööööö/                         /ööööö|          " + "\n" \
    r"                              /ööööööööööööööööööö/                         /öööööö|          " + "\n" \
    r"                             /ööööööööööööööööööö/                         /ööööööö|          " + "\n" \
    r"              X-------------Xööööööööööööööööööö(                         /öööööööö|          " + "\n" \
    r"             /ööööööööööööööööööööööööööööööööööö\                       /ööööööööö|          " + "\n" \
    r"            /ööööööööööööööööööööööööööööööööööööö\                     /öööööööööö|          " + "\n" \
    r"           /ööööööööWöööööööööööööööööööööööööööööö--------------------Xööööööööööö|          " + "\n" \
    r"          |öööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö|          " + "\n" \
    r"          |ööSööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö|          " + "\n" \
    r"          |öööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö|          " + "\n" \
    r"           \ööööööööööööööööööööööööööööööööööööööö--------------------Xööööööööööö|          " + "\n" \
    r"            \ööööööööööööööööööööööööööööööööööööö/                     \öööööööööö|          " + "\n" \
    r"             \ööööööööööö1ööööööööööööööööööööööö/                       \ööööööööö|          " + "\n" \
    r"              X-------------Xööööööööööööööööööö(                         \öööööööö|          " + "\n" \
    r"                             \ööööööööööööööööööö\                         \ööööööö|          " + "\n" \
    r"                              \ööööööööööööööööööö\                         \öööööö|          " + "\n" \
    r"                               \ööööööööööööööööööö\                         \ööööö|          " + "\n" \
    r"                                |ööööööööööööööööööö\                         \öööö|          " + "\n" \
    r"                                |öööööööööööööööööööö)>                        \ööö|          " + "\n" \
    r"                                |öööööööööööööööööööö)>                         \öö|          " + "\n" \
    r"                                 \ööööööööööööööööööö)>                          \ö|          " + "\n" \
    r"                                  \öööööööööööööööööö)>                           \)          " + "\n" \
    r"                                   \ööööööööGöööööööö)>                                       " + "\n" \
    r"                                    X---------------X                                         " + "\n" \
    r"                                                                                              " + "\n" \



__rm = random.Random()
def spaceship_random() -> float:
    return __rm.random()


class SpaceshipWallTile(Tile):
    MAP_INVISIBLE_PRESENTATION = "X"

    def __init__(self, character):
        super(SpaceshipWallTile, self).__init__(TileCode.SpaceshipBlock)
        self.__img = character

    def get_img(self):
        return self.__img

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False

    def __str__(self):
        return "W"


class SpaceshipFreeWalkTile(Tile):
    MAP_REPRESENTATION = "ö"

    def __init__(self):
        super(SpaceshipFreeWalkTile, self).__init__(TileCode.SpaceshipWalk)

    def get_img(self):
        #return ColorConfig.colorize(ColorCodes.SPACESHIP_FLOOR, self._invisible)
        return "."#self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True

    def __str__(self):
        return "f"


class SpaceshipTriggerTile(WalkTriggerTile):
    MAP_START_REPRESENTATION = "S"
    MAP_WORKBENCH_REPRESENTATION = "W"
    MAP_GATE_LIBRARY_REPRESENTATION = "G"
    START_TUTORIAL = "1"

    def __init__(self, character: str, callback: Callable[[Direction, Robot], None]):
        super().__init__(TileCode.SpaceshipTrigger)
        self.__img = character
        self.__callback = callback

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__callback(direction, robot)

    def get_img(self):
        return self.__img


class OuterSpaceTile(Tile):
    MAP_REPRESENTATION = " "
    __STAR_BIRTH_CHANCE = 0.0001
    __STAR_DIE_CHANCE = 0.01

    def __init__(self):
        super(OuterSpaceTile, self).__init__(TileCode.OuterSpace)
        self.__is_star = spaceship_random() < 0.007

    def get_img(self):
        if self.__is_star:
            if spaceship_random() < OuterSpaceTile.__STAR_DIE_CHANCE:
                self.__is_star = False
            return "*"
        else:
            if spaceship_random() < OuterSpaceTile.__STAR_BIRTH_CHANCE:
                self.__is_star = True
            return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False

    def __str__(self):
        return "o"


class SpaceshipMap:
    WIDTH = ascii_spaceship.index("\n")
    HEIGHT = ascii_spaceship.count("\n")
    SPAWN_POS = Coordinate(x=25, y=16)

    def __init__(self, seed: int, player: Player, open_world_view: Callable[[Direction, Controllable], None],
                 use_workbench: Callable[[Direction, Controllable], None],
                 start_tutorial: Callable[[Direction, Controllable], None]):
        self.__rm = MyRandom(seed)
        self.__player = player
        self.__open_world_view = open_world_view
        self.__use_workbench = use_workbench
        self.__start_tutorial = start_tutorial
        self.__tiles = []
        row = []
        for character in ascii_spaceship:
            if character == "\n":
                self.__tiles.append(row)
                row = []
            else:
                tile = self.__ascii_to_tile(character)
                row.append(tile)

        self.__player_pos = SpaceshipMap.SPAWN_POS

        # self.widget.activate_custom_draw()

    @property
    def player_pos(self) -> Coordinate:
        return self.__player_pos

    def __ascii_to_tile(self, character: str) -> Tile:
        if character == SpaceshipFreeWalkTile.MAP_REPRESENTATION:
            tile = SpaceshipFreeWalkTile()
        elif character == OuterSpaceTile.MAP_REPRESENTATION:
            tile = OuterSpaceTile()
        elif character == SpaceshipWallTile.MAP_INVISIBLE_PRESENTATION:
            tile = SpaceshipWallTile(" ")
        elif character == SpaceshipTriggerTile.MAP_START_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.__open_world_view)
        elif character == SpaceshipTriggerTile.MAP_WORKBENCH_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.__use_workbench)
        # elif character == SpaceshipTriggerTile.MAP_GATE_LIBRARY_REPRESENTATION:
        #    tile = SpaceshipTriggerTile(character, self.open_gate_library)
        elif character == SpaceshipTriggerTile.START_TUTORIAL:
            tile = SpaceshipTriggerTile(character, self.__start_tutorial)
        else:
            tile = SpaceshipWallTile(character)
        return tile

    @property
    def width(self) -> int:
        return SpaceshipMap.WIDTH

    @property
    def height(self) -> int:
        return SpaceshipMap.HEIGHT

    def move(self, direction: Direction) -> bool:
        """
        Tries to move the player in the given Direction.
        :param direction: in which direction the player should move
        :return: True if the player was able to move, False otherwise
        """
        new_pos = self.__player_pos + direction
        if new_pos.y < 0 or self.height <= new_pos.y or \
                new_pos.x < 0 or self.width <= new_pos.x:
            return False

        tile = self.__tiles[new_pos.y][new_pos.x]
        if tile.is_walkable(direction, self.__player):
            if isinstance(tile, WalkTriggerTile):
                tile.trigger(direction, self.__player, self.__trigger_event)
            self.__player_pos = new_pos
            return True
        else:
            return False

    def __trigger_event(self, event_id: str):
        # todo check if we really don't need this in the Spaceship
        pass

    def get_row_strings(self) -> List[str]:
        rows = []
        for row in self.__tiles:
            cur_row = ""
            for tile in row:
                cur_row += tile.get_img()
            rows.append(cur_row)
        return rows
