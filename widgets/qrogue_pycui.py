from enum import Enum

import py_cui

from game.actors.enemy import Enemy
from game.actors.player import Player as PlayerActor
from game.controls import Controls
from game.map.map import Map
from game.map.navigation import Direction
from util.logger import Logger
from widgets.widget_sets import ExploreWidgetSet, FightWidgetSet, MyWidgetSet, MenuWidgetSet


class QrogueCUI(py_cui.PyCUI):
    def __init__(self, seed: int, controls: Controls, width: int = 8, height: int = 9):
        super().__init__(width, height)
        Logger.instance().set_popup(self.show_message_popup, self.show_error_popup)
        self.__state_machine = StateMachine(self)
        self.__seed = seed
        self.__controls = controls

        self.__menu = MenuWidgetSet(Logger.instance(), self.__start_gameplay, self.__start_fight)
        self.__explore = ExploreWidgetSet(Logger.instance())
        self.__fight = FightWidgetSet(Logger.instance(), self.continue_explore)

        self.__cur_widget_set = None
        self.__init_keys()

        self.__state_machine.change_state(State.Menu, None)
        self.render()

    def __init_keys(self):
        # debugging stuff
        self.add_key_command(self.__controls.print_screen, self.print_screen)
        self.__menu.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__explore.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__fight.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)

        # all selections
        selection_widgets = [self.__menu.selection, self.__fight.choices, self.__fight.details]
        for my_widget in selection_widgets:
            widget = my_widget.widget
            widget.add_key_command(self.__controls.selection_up, my_widget.up)
            widget.add_key_command(self.__controls.selection_right, my_widget.right)
            widget.add_key_command(self.__controls.selection_down, my_widget.down)
            widget.add_key_command(self.__controls.selection_left, my_widget.left)

        # menu
        self.__menu.selection.widget.add_key_command(self.__controls.action, self.__use_menu_selection)

        # explore
        w = self.__explore.get_main_widget()
        w.add_key_command(self.__controls.move_up, self.__explore.move_up)
        w.add_key_command(self.__controls.move_right, self.__explore.move_right)
        w.add_key_command(self.__controls.move_down, self.__explore.move_down)
        w.add_key_command(self.__controls.move_left, self.__explore.move_left)

        # fight
        self.__fight.choices.widget.add_key_command(self.__controls.action, self.__use_choice)
        self.__fight.details.widget.add_key_command(self.__controls.action, self.__use_details)

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

    def apply_widget_set(self, new_widget_set: MyWidgetSet):
        new_widget_set.reset()
        super().apply_widget_set(new_widget_set)
        self.__cur_widget_set = new_widget_set
        self.__cur_widget_set.activate_logger()
        self.move_focus(self.__cur_widget_set.get_main_widget(), auto_press_buttons=False)
        self.__cur_widget_set.render()

    def switch_to_menu(self, data):
        self.apply_widget_set(self.__menu)

    def __start_gameplay(self, map: Map):
        self.__state_machine.change_state(State.Explore, map)

    def __start_fight(self, player: PlayerActor, enemy: Enemy, direction: Direction):
        self.__state_machine.change_state(State.Fight, (enemy, player))

    def switch_to_explore(self, data):
        if data is not None:
            map = data
            self.__explore.set_data(map, map.player)
        self.apply_widget_set(self.__explore)

    def continue_explore(self):
        self.__state_machine.change_state(State.Explore, None)

    def switch_to_fight(self, data):
        enemy = data[0]
        player = data[1]
        enemy.fight_init(player)
        self.__fight.set_data(player, enemy)
        self.apply_widget_set(self.__fight)

    def render(self):
        self.__cur_widget_set.render()

    def __use_menu_selection(self):
        if self.__menu.selection.use() and self.__cur_widget_set is self.__menu:
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


class State(Enum):
    Menu = 0
    Pause = 1
    Explore = 2
    Fight = 3
    Riddle = 4


class StateMachine:
    def __init__(self, renderer: QrogueCUI):
        self.__renderer = renderer
        self.__cur_state = None
        self.__prev_state = None

    @property
    def cur_state(self):
        return self.__cur_state

    @property
    def prev_state(self):
        return self.__prev_state

    def change_state(self, state: State, data):
        self.__prev_state = self.__cur_state
        self.__cur_state = state

        if self.__cur_state == State.Menu:
            self.__renderer.switch_to_menu(data)
        elif self.__cur_state == State.Explore:
            self.__renderer.switch_to_explore(data)
        elif self.__cur_state == State.Fight:
            self.__renderer.switch_to_fight(data)
        #elif self.__cur_state == State.Pause:
        #    self.__game.init_pause_screen()
        #elif self.__cur_state == State.Riddle:
        #    self.__game.init_riddle_screen()
