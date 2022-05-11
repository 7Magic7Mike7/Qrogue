from typing import Callable, List

import py_cui

from qrogue.game.world.map import SpaceshipMap
from qrogue.game.world.navigation import Direction
from qrogue.graphics.rendering import ColorRules
from qrogue.util import Controls, Keys, UIConfig

from qrogue.graphics.widgets import MyBaseWidget, MyWidgetSet, Renderable, Widget


class SpaceshipWidget(Widget):
    def __init__(self, widget: MyBaseWidget):
        super().__init__(widget)
        self.__spaceship_map = None
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


class SpaceshipWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None]):
        super().__init__(logger, root, base_render_callback)

        spaceship = self.add_block_label("Dynamic Spaceship", 0, 0, UIConfig.WINDOW_HEIGHT, UIConfig.WINDOW_WIDTH,
                                         center=True)
        spaceship.add_key_command(controls.get_keys(Keys.MoveUp), self.move_up)
        spaceship.add_key_command(controls.get_keys(Keys.MoveRight), self.move_right)
        spaceship.add_key_command(controls.get_keys(Keys.MoveDown), self.move_down)
        spaceship.add_key_command(controls.get_keys(Keys.MoveLeft), self.move_left)
        self.__spaceship = SpaceshipWidget(spaceship)

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
