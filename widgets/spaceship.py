import random

import py_cui

from game.actors.robot import Robot, Testbot
from game.callbacks import CallbackPack
from game.controls import Controls
from game.expedition import Expedition
from game.map import tiles
from game.map.navigation import Direction, Coordinate
from game.map.tiles import WalkTriggerTile, TileCode
from game.map.tutorial import Tutorial
from game.save_data import SaveData
from util.config import ColorCode, ColorConfig
from util.logger import Logger
from widgets.my_widgets import Widget, MyBaseWidget
from widgets.widget_sets import MyWidgetSet

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
    r"             \ööööööööööööööööööööööööööööööööööö/                       \ööööööööö|          " + "\n" \
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


class SpaceshipWallTile(tiles.Tile):
    MAP_INVISIBLE_PRESENTATION = "X"

    def __init__(self, character):
        super(SpaceshipWallTile, self).__init__(tiles.TileCode.SpaceshipBlock)
        self.__img = character

    def get_img(self):
        return self.__img

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False

    def __str__(self):
        return "W"


class SpaceshipFreeWalkTile(tiles.Tile):
    MAP_REPRESENTATION = "ö"

    def __init__(self):
        super(SpaceshipFreeWalkTile, self).__init__(tiles.TileCode.SpaceshipWalk)

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

    def __init__(self, character: str, callback: (Direction, Robot)):
        super().__init__(TileCode.SpaceshipTrigger)
        self.__img = character
        self.__callback = callback

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__callback(direction, robot)

    def get_img(self):
        return self.__img


class OuterSpaceTile(tiles.Tile):
    MAP_REPRESENTATION = " "
    __STAR_BIRTH_CHANCE = 0.0001
    __STAR_DIE_CHANCE = 0.01

    def __init__(self):
        super(OuterSpaceTile, self).__init__(tiles.TileCode.OuterSpace)
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


class SpaceshipWidget(Widget):
    WIDTH = ascii_spaceship.index("\n")
    HEIGHT = ascii_spaceship.count("\n")

    def __init__(self, widget: MyBaseWidget, cbp: CallbackPack, seed: int, save_data: SaveData):
        super().__init__(widget)

        self.__cbp = cbp
        self.__seed = seed
        self.__use_workbench = None
        self.__tiles = []
        row = []
        for character in ascii_spaceship:
            if character == "\n":
                self.__tiles.append(row)
                row = []
            else:
                tile = self.__ascii_to_tile(character)
                row.append(tile)

        self.__player_tile = None
        self.__player_pos = None

        self.__save_data = save_data
        if self.__save_data.played_tutorial():
            self.__cur_expedition = Expedition(self.__cbp)
        else:
            self.__cur_expedition = Tutorial(self.__cbp)

        self.__cur_expedition.set_seed(self.__seed)     # todo set in navigation field later
        self.__cur_expedition.set_robot(Testbot(self.__seed))   # todo set in workshop later

        self.widget.add_text_color_rule('\.', ColorConfig.get_from_code(ColorCode.SPACESHIP_FLOOR), 'contains',
                                        match_type='regex')
        self.widget.add_text_color_rule('(P|R)', ColorConfig.get_from_code(ColorCode.SPACESHIP_FLOOR), 'contains',
                                        match_type='regex')
        self.widget.add_text_color_rule('(S|W|N)', ColorConfig.get_from_code(ColorCode.SPACESHIP_FLOOR), 'contains',
                                        match_type='regex')

        #self.widget.activate_custom_draw()

    def __ascii_to_tile(self, character: str) -> tiles.Tile:
        if character == SpaceshipFreeWalkTile.MAP_REPRESENTATION:
            tile = SpaceshipFreeWalkTile()
        elif character == OuterSpaceTile.MAP_REPRESENTATION:
            tile = OuterSpaceTile()
        elif character == SpaceshipWallTile.MAP_INVISIBLE_PRESENTATION:
            tile = SpaceshipWallTile(" ")
        elif character == SpaceshipTriggerTile.MAP_START_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.start_expedition)
        elif character == SpaceshipTriggerTile.MAP_WORKBENCH_REPRESENTATION:
            tile = SpaceshipTriggerTile(character, self.use_workbench)
        #elif character == SpaceshipTriggerTile.MAP_GATE_LIBRARY_REPRESENTATION:
        #    tile = SpaceshipTriggerTile(character, self.open_gate_library)
        else:
            tile = SpaceshipWallTile(character)
        return tile

    @property
    def width(self) -> int:
        return SpaceshipWidget.WIDTH

    @property
    def height(self) -> int:
        return SpaceshipWidget.HEIGHT

    def set_data(self, data: (tiles.RobotTile, ())) -> None:
        self.__player_tile = data[0]
        self.__player_pos = Coordinate(x=25, y=16)
        self.__use_workbench = data[1]
        self.render()

    def render(self) -> None:
        #str_rep = ascii_spaceship
        str_rep = ""
        for row in self.__tiles:
            for tile in row:
                str_rep += tile.get_img()
            str_rep += "\n"
        if self.__player_tile is not None and self.__player_pos is not None:
            # add player on top
            player_index = self.__player_pos.x + self.__player_pos.y * (SpaceshipWidget.WIDTH + 1)  # +1 because of the \n at the end
            str_rep = str_rep[:player_index] + self.__player_tile.get_img() + str_rep[player_index + 1:]

        self.widget.set_title(str_rep)

    def render_reset(self) -> None:
        pass

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
        if tile.is_walkable(direction, self.__player_tile.robot):
            if isinstance(tile, tiles.WalkTriggerTile):
                tile.on_walk(direction, self.__player_tile.robot)
            self.__player_pos = new_pos
            return True
        else:
            return False

    def start_expedition(self, direction: Direction, robot: Robot):
        if not self.__cur_expedition.start():
            Logger.instance().throw(ValueError(f"Illegal state! No expedition can be started for seed = {self.__seed}!"))

    def use_workbench(self, direction: Direction, robot: Robot):
        self.__use_workbench(self.__save_data)


class SpaceshipWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI, base_render_callback: "()", cbp: CallbackPack,
                 seed: int, save_data: SaveData):
        self.__cbp = cbp
        self.__seed = seed
        self.__save_data = save_data
        super().__init__(controls, logger, root, base_render_callback)

    def init_widgets(self, controls: Controls) -> None:
        spaceship = self.add_block_label("Dynamic Spaceship", 0, 0, MyWidgetSet.NUM_OF_ROWS, MyWidgetSet.NUM_OF_COLS,
                                         center=True)
        self.__spaceship = SpaceshipWidget(spaceship, self.__cbp, self.__seed, self.__save_data)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__spaceship,
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__spaceship.widget

    def reset(self) -> None:
        pass

    def set_data(self, data: (tiles.RobotTile, ())):
        self.__spaceship.set_data(data)

    def move_up(self):
        if self.__spaceship.move(Direction.Up):
            self.render()

    def move_right(self):
        if self.__spaceship.move(Direction.Right):
            self.render()

    def move_down(self):
        if self.__spaceship.move(Direction.Down):
            self.render()

    def move_left(self):
        if self.__spaceship.move(Direction.Left):
            self.render()
