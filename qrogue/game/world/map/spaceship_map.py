import random
from typing import Callable, List

from qrogue.game.logic.actors import Robot, Controllable, Player
from qrogue.game.world.navigation import Direction, Coordinate
from qrogue.game.world.tiles import Tile, TileCode, WalkTriggerTile
from qrogue.game.world.tiles.tiles import NpcTile
from qrogue.util import MyRandom, Config, MapConfig, achievements

SCIENTIST_TILE_REPRESENTATION = Config.scientist_name()[0]
ascii_spaceship = \
    r"                                                                                              " + "\n" \
    r"                                    X---------------X                                         " + "\n" \
    r"                                   /ööööööööööööööööö)>                                       " + "\n" \
    r"                                  /öööööööBöööööööööö)>                           /)          " + "\n" \
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
    r"          |ööNööööööööööRöööööööööööööööööööööööööööööööööööööööööööööööööööööööööö|          " + "\n" \
    r"          |öööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö|          " + "\n" \
    r"           \ööööööööööööööööööööööööööööööööööööööö--------------------Xööööööööööö|          " + "\n" \
    r"            \ööööööööööööööööööööööööööööööööööööö/                     \öööööööööö|          " + "\n" \
    r"             \öööööööööööQööööööööööööööööööööööö/                       \ööööööööö|          " + "\n" \
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
def _spaceship_random() -> float:
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

    def copy(self) -> "Tile":
        return SpaceshipWallTile(self.__img)

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

    def copy(self) -> "Tile":
        return SpaceshipFreeWalkTile()

    def __str__(self):
        return "f"


class SpaceshipTriggerTile(WalkTriggerTile):
    BED_SPAWN_REPRESENTATION = "B"
    MAP_START_REPRESENTATION = "N"
    MAP_WORKBENCH_REPRESENTATION = "W"
    MAP_GATE_LIBRARY_REPRESENTATION = "G"
    QUICKSTART_LEVEL = "Q"      # Quickstart

    def __init__(self, character: str, callback: Callable[[Direction, Robot], None]):
        super().__init__(TileCode.SpaceshipTrigger)
        self.__img = character
        self.__callback = callback

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__callback(direction, robot)

    def get_img(self):
        return self.__img

    def _copy(self) -> "Tile":
        return SpaceshipTriggerTile(self.__img, self.__callback)


class OuterSpaceTile(Tile):
    MAP_REPRESENTATION = " "
    __STAR_BIRTH_CHANCE = 0.0001
    __STAR_DIE_CHANCE = 0.01

    def __init__(self):
        super(OuterSpaceTile, self).__init__(TileCode.OuterSpace)
        self.__is_star = _spaceship_random() < 0.007

    def get_img(self):
        if self.__is_star:
            if _spaceship_random() < OuterSpaceTile.__STAR_DIE_CHANCE:
                self.__is_star = False
            return "*"
        else:
            if _spaceship_random() < OuterSpaceTile.__STAR_BIRTH_CHANCE:
                self.__is_star = True
            return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False

    def copy(self) -> "Tile":
        return OuterSpaceTile()

    def __str__(self):
        return "o"


class SpaceshipMap:
    WIDTH = ascii_spaceship.index("\n")
    HEIGHT = ascii_spaceship.count("\n")
    SPAWN_POS = Coordinate(x=25, y=16)

    def __init__(self, seed: int, player: Player, scientist: NpcTile, check_achievement: Callable[[str], bool],
                 stop_playing: Callable[[Direction, Controllable], None],
                 open_world_view: Callable[[Direction, Controllable], None],
                 use_workbench: Callable[[Direction, Controllable], None],
                 load_map: Callable[[str, Coordinate], None]):
        self.__rm = MyRandom(seed)
        self.__player = player
        self.__scientist = scientist
        self.__check_achievement = check_achievement
        self.__stop_playing_callback = stop_playing
        self.__open_world_view = open_world_view
        self.__use_workbench_callback = use_workbench
        self.__load_map = load_map
        self.__tiles = []
        row = []
        for character in ascii_spaceship:
            if character == "\n":
                self.__tiles.append(row)
                row = []
            else:
                if character == SpaceshipTriggerTile.BED_SPAWN_REPRESENTATION:
                    # we want to start on top of the bed
                    SpaceshipMap.SPAWN_POS = Coordinate(len(row), len(self.__tiles))
                tile = self.__ascii_to_tile(character)
                row.append(tile)

        self.__player_pos = SpaceshipMap.SPAWN_POS

        # self.widget.activate_custom_draw()

    @property
    def player_pos(self) -> Coordinate:
        return self.__player_pos

    def __ascii_to_tile(self, character: str) -> Tile:
        if character == SCIENTIST_TILE_REPRESENTATION:
            tile = self.__scientist
        elif character == SpaceshipFreeWalkTile.MAP_REPRESENTATION:
            tile = SpaceshipFreeWalkTile()
        elif character == OuterSpaceTile.MAP_REPRESENTATION:
            tile = OuterSpaceTile()
        elif character == SpaceshipWallTile.MAP_INVISIBLE_PRESENTATION:
            tile = SpaceshipWallTile(" ")
        elif character == SpaceshipTriggerTile.BED_SPAWN_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.__stop_playing)
        elif character == SpaceshipTriggerTile.MAP_START_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.__open_world_view)
        elif character == SpaceshipTriggerTile.MAP_WORKBENCH_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.__use_workbench)
        # elif character == SpaceshipTriggerTile.MAP_GATE_LIBRARY_REPRESENTATION:
        #    tile = SpaceshipTriggerTile(character, self.open_gate_library)
        elif character == SpaceshipTriggerTile.QUICKSTART_LEVEL:
            if Config.debugging():
                def start_test_level(direction: Direction, controllable: Controllable):
                    self.__load_map(MapConfig.test_level(), None)
                tile = SpaceshipTriggerTile(character, start_test_level)
            else:
                def start_newest_level(direction: Direction, controllable: Controllable):
                    self.__load_map(MapConfig.spaceship(), None)
                tile = SpaceshipTriggerTile(character, start_newest_level)
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

    def __stop_playing(self, direction: Direction, controllable: Controllable):
        if self.__check_achievement(achievements.FinishedTutorial):
            self.__stop_playing_callback(direction, controllable)

    def __use_workbench(self, direction: Direction, controllable: Controllable):
        if self.__check_achievement(achievements.UnlockedWorkbench):
            self.__use_workbench_callback(direction, controllable)

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
