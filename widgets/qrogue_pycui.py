
import py_cui

from game.actors.enemy import Enemy
from game.controls import Controls
from game.map.map import Map
from game.map.navigation import Direction
from game.map.tiles import Player as PlayerTile
from util.logger import Logger
from widgets.widget_sets import ExploreWidgetSet, FightWidgetSet, MyWidgetSet


class QrogueCUI(py_cui.PyCUI):
    def __init__(self, seed: int, controls: Controls, end_of_fight_callback, width: int = 8, height: int = 9):
        super().__init__(width, height)
        self.__map = None
        self.__seed = seed
        self.__controls = controls

        self.__explore = ExploreWidgetSet(Logger.instance())
        self.__fight = FightWidgetSet(Logger.instance(), self.continue_explore)

        self.__cur_widget_set = self.__explore
        self.__init_keys()

    def __init_keys(self):
        self.add_key_command(py_cui.keys.KEY_R_LOWER, self.manual_refocus)
        self.add_key_command(self.__controls.print_screen, self.print_screen)

        self.__explore.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__fight.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)

        w = self.__explore.get_main_widget()
        w.add_key_command(self.__controls.move_up, self.__move_up)
        w.add_key_command(self.__controls.move_right, self.__move_right)
        w.add_key_command(self.__controls.move_down, self.__move_down)
        w.add_key_command(self.__controls.move_left, self.__move_left)

        selection_widgets = [self.__fight.choices, self.__fight.details]
        for my_widget in selection_widgets:
            widget = my_widget.widget
            widget.add_key_command(self.__controls.selection_up, my_widget.up)
            widget.add_key_command(self.__controls.selection_right, my_widget.right)
            widget.add_key_command(self.__controls.selection_down, my_widget.down)
            widget.add_key_command(self.__controls.selection_left, my_widget.left)

        self.__fight.choices.widget.add_key_command(self.__controls.action, self.__use_choice)
        self.__fight.details.widget.add_key_command(self.__controls.action, self.__use_details)

    def manual_refocus(self):
        self.refocus()

    def print_screen(self):
        import os
        from datetime import datetime
        folder = os.path.join("Documents", "Studium", "Master", "3. Semester", "Qrogue", "screenprints")
        now = datetime.now()
        now_str = now.strftime("%d%m%Y_%H%M%S")
        file_name = f"screenshot_{now_str}.qrogue_screen"

        text = now_str + "\n"
        for my_widget in self.__cur_widget_set.get_widget_list():
            text += str(my_widget) + "\n"
            text += my_widget.widget.get_title()
            text += "\n"

        file = open("D:\\" + os.path.join(folder, file_name), "x")  # todo use config for path!
        file.write(text)
        file.close()

    def refocus(self):
        # apparently we have to manually set and reset the focus for keys to work
        self.lose_focus()
        self.move_focus(self.__cur_widget_set.get_main_widget(), auto_press_buttons=False)

    def apply_widget_set(self, new_widget_set: MyWidgetSet):
        new_widget_set.reset()
        super().apply_widget_set(new_widget_set)
        self.__cur_widget_set = new_widget_set
        self.__cur_widget_set.activate_logger()
        self.__cur_widget_set.render()

    def switch_to_explore(self, map: Map, player_tile: PlayerTile):
        self.__map = map
        self.__explore.set_data(map, player_tile)
        self.apply_widget_set(self.__explore)
        self.refocus()

    def continue_explore(self): # todo check if this is better than the callback of game
        self.apply_widget_set(self.__explore)
        self.refocus()

    def switch_to_fight(self, player_tile: PlayerTile, enemy: Enemy):
        enemy.fight_init(player_tile.player)
        self.__fight.set_data(player_tile, enemy)
        self.apply_widget_set(self.__fight)
        self.move_focus(self.__fight.choices.widget)

    def render(self):
        self.__cur_widget_set.render()

    # key kommand methods
    def __move_up(self):
        if self.__map.move(Direction.Up):
            self.render()

    def __move_right(self):
        if self.__map.move(Direction.Right):
            self.render()

    def __move_down(self):
        if self.__map.move(Direction.Down):
            self.render()

    def __move_left(self):
        if self.__map.move(Direction.Left):
            self.render()

    def __use_choice(self):
        if self.__fight.choices.use() and self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.details.widget, auto_press_buttons=False)
            self.__fight.choices.render()
            self.__fight.details.render()

    def __use_details(self):
        if self.__fight.details.use() and self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.choices.widget, auto_press_buttons=False)
            self.__fight.render()   # needed for updating the StateVectors and the circuit
