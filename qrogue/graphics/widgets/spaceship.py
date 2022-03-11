from typing import Callable, List

import py_cui

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.map import SpaceshipMap
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.graphics.rendering import ColorRules
from qrogue.util import Controls, MapConfig

from qrogue.graphics.widgets import MyBaseWidget, MyWidgetSet, Renderable, Widget


class SpaceshipWidget(Widget):
    def __init__(self, widget: MyBaseWidget, seed: int, load_map: Callable[[str, Coordinate], None]):
        super().__init__(widget)
        self.__load_map = load_map
        self.__use_workbench_callback = None
        self.__spaceship_map = None #SpaceshipMap(seed, self.__player, self.__open_world_view, self.__use_workbench,
                                    #        self.__start_tutorial)
        ColorRules.apply_spaceship_rules(widget)

    def set_data(self, data: SpaceshipMap) -> None:
        self.__spaceship_map = data
        self.render()

    def render(self) -> None:
        if self.__spaceship_map:
            rows = self.__spaceship_map.get_row_strings()
            # add player on top
            x = self.__spaceship_map.player_pos.x
            y = self.__spaceship_map.player_pos.y
            rows[y] = rows[y][0:x] + "M" + rows[y][x + 1:]  # todo fix player-img
            self.widget.set_title("\n".join(rows))

    def render_reset(self) -> None:
        pass

    def move(self, direction: Direction) -> bool:
        """
        Tries to move the player in the given Direction.
        :param direction: in which direction the player should move
        :return: True if the player was able to move, False otherwise
        """
        return self.__spaceship_map.move(direction)

    def __open_world_view(self, direction: Direction, controllable: Controllable):
        self.__load_map(MapConfig.hub_world(), None)

    def __use_workbench(self, direction: Direction, controllable: Controllable):
        self.__use_workbench_callback()

    def __start_tutorial(self, direction: Direction, controllable: Controllable):
        self.__load_map(MapConfig.tutorial_level(), None)


class SpaceshipWidgetSet(MyWidgetSet):
    def __init__(self, seed: int, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None], load_map: Callable[[str, Coordinate], None]):
        self.__seed = seed
        self.__load_map = load_map
        super().__init__(controls, logger, root, base_render_callback)

    def init_widgets(self, controls: Controls) -> None:
        spaceship = self.add_block_label("Dynamic Spaceship", 0, 0, MyWidgetSet.NUM_OF_ROWS, MyWidgetSet.NUM_OF_COLS,
                                         center=True)
        self.__spaceship = SpaceshipWidget(spaceship, self.__seed, self.__load_map)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__spaceship,
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__spaceship.widget

    def reset(self) -> None:
        pass

    def set_data(self, data: SpaceshipMap):
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
