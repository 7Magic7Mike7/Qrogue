from abc import abstractmethod

import py_cui
from py_cui.widget_set import WidgetSet

from game.actors.enemy import Enemy
from game.controls import Controls
from game.map.navigation import Direction
from game.map.tiles import Player as PlayerTile
from util.logger import Logger
from widgets.color_rules import ColorRules
from widgets.my_widgets import *


class MyWidgetSet(WidgetSet):
    def __init__(self, num_rows, num_cols, logger):
        super().__init__(num_rows, num_cols, logger)
        self.init_widgets()

    def render(self):
        for widget in self.get_widget_list():
            widget.render()

    @abstractmethod
    def init_widgets(self):
        pass

    @abstractmethod
    def activate_logger(self):
        pass

    @abstractmethod
    def get_widget_list(self) -> "list of Widgets":
        pass

    @abstractmethod
    def get_main_widget(self) -> py_cui.widgets.Widget:
        pass

    @abstractmethod
    def reset(self):
        pass


class ExploreWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 8
    __NUM_OF_COLS = 9

    def __init__(self, logger):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__map = None
        self.__player_tile = None
        self.__first_row = self.add_block_label('first line (metadata like playtime, floor, ...?)', 0, 0,
                                         column_span=self.__NUM_OF_COLS)
        self.__first_row.toggle_border()

    def init_widgets(self):
        map_widget = self.add_block_label('MAP', 1, 2, row_span=5, column_span=5, center=True)
        #map_widget.toggle_border()
        self.__main_widget = MapWidget(map_widget)

        player_info_widget = self.add_block_label('Player', 1, 0, row_span=5, column_span=2, center=True)
        #player_info_widget.toggle_border()
        self.__left_widget = PlayerInfoWidget(player_info_widget)

        qubits_widget = self.add_block_label('Qubits life & state', 6, 0, row_span=2, column_span=2, center=True)
        #qubits_widget.toggle_border()
        self.__left_bottom_widget = PlayerQubitsWidget(qubits_widget)

        circuit_widget = self.add_block_label('Circuit', 6, 2, row_span=2, column_span=5, center=True)
        #circuit_widget.toggle_border()
        self.__bottom_widget = CircuitWidget(circuit_widget)

        event_info_widget = self.add_block_label('Enemy/Event', 1, 7, row_span=5, column_span=2, center=True)
        #event_info_widget.toggle_border()
        self.__right_widget = EventInfoWidget(event_info_widget)

        event_targets_widget = self.add_block_label('Event targets', 6, 7, row_span=2, column_span=2, center=True)
        #event_targets_widget.toggle_border()
        self.__right_bottom_widget = EventQubitsWidget(event_targets_widget)

        ColorRules.apply_map_rules(self.__main_widget)

    def activate_logger(self):
        Logger.instance().set_label(self.__first_row)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__main_widget.widget

    def set_data(self, map: Map, player_tile: PlayerTile):
        self.__map = map
        self.__player_tile = player_tile
        self.__main_widget.set_data(map)
        self.__bottom_widget.set_data(player_tile)
        self.__left_widget.set_data(player_tile)
        self.__left_bottom_widget.set_data(player_tile)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__main_widget,
            self.__bottom_widget,
            self.__left_widget,
            self.__left_bottom_widget
        ]

    def reset(self):
        self.__main_widget.widget.set_title("")


class FightWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9

    def __init__(self, logger, end_of_fight_callback):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__player = None
        self.__enemy = None
        self.__end_of_fight_callback = end_of_fight_callback

    def init_widgets(self):
        logger_row = self.add_block_label('Logger', 0, 0, row_span=1, column_span=self.__NUM_OF_COLS, center=True)
        logger_row.toggle_border()
        self.__logger_row = logger_row

        stv_row = 1
        stv = self.add_block_label('Player StV', stv_row, 0, row_span=4, column_span=3, center=True)
        self.__stv_player = StateVectorWidget(stv, "Current State")
        stv = self.add_block_label('Diff StV', stv_row, 3, row_span=3, column_span=3, center=True)
        self.__stv_diff = StateVectorWidget(stv, "Difference")
        stv = self.add_block_label('Enemy StV', stv_row, 6, row_span=3, column_span=3, center=True)
        self.__stv_enemy = StateVectorWidget(stv, "Target State")

        circuit = self.add_block_label('Circuit', 5, 0, row_span=2, column_span=self.__NUM_OF_COLS, center=True)
        circuit.toggle_border()
        self.__circuit = CircuitWidget(circuit)

        choices = self.add_block_label('Choices', 7, 0, row_span=2, column_span=3, center=True)
        choices.toggle_border()
        self.__choices = SelectionWidget(choices, columns=SelectionWidget.FIGHT_CHOICE_COLUMNS)
        self.__choices.set_data(data=(
            ["Adapt", "Commit", "Items", "Flee"],
            [self.__choices_adapt, self.__choices_commit, self.__choices_items, self.__choices_flee]
        ))

        details = self.add_block_label('Details', 7, 3, row_span=2, column_span=6, center=True)
        details.toggle_border()
        self.__details = SelectionWidget(details, columns=SelectionWidget.FIGHT_DETAILS_COLUMNS)

        ColorRules.apply_stv_rules(self.__stv_player)
        ColorRules.apply_stv_rules(self.__stv_diff, diff_rules=True)
        ColorRules.apply_stv_rules(self.__stv_enemy)
        ColorRules.apply_circuit_rules(self.__circuit)
        ColorRules.apply_selection_rules(self.__choices)
        ColorRules.apply_selection_rules(self.__details)

    def activate_logger(self):
        Logger.instance().set_label(self.__logger_row)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__choices.widget

    def set_data(self, player_tile: PlayerTile, enemy: Enemy):
        self.__player = player_tile.player
        self.__enemy = enemy

        self.__circuit.set_data(player_tile)

        p_stv = player_tile.player.state_vector
        e_stv = enemy.get_statevector()
        self.__stv_player.set_data(p_stv)
        self.__stv_diff.set_data(p_stv.get_diff(e_stv))
        self.__stv_enemy.set_data(e_stv)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__stv_player,
            self.__stv_diff,
            self.__stv_enemy,
            self.__circuit,
            self.__choices,
            self.__details
        ]

    def reset(self):
        Logger.instance().println("Is there something to reset?", clear=True)

    @property
    def choices(self):
        return self.__choices

    @property
    def details(self):
        return self.__details

    def __choices_adapt(self) -> bool:
        self.__details.set_data(data=(
            [str(instruction) for instruction in self.__player.backpack],
            [self.__player.use_instruction]
        ))
        return True

    def __choices_commit(self) -> bool:
        if self.attack():
            self.__details.set_data(data=(
                ["Get reward! TODO implement"],
                [self.__end_of_fight_callback]
            ))
            return True
        return False

    def __choices_items(self) -> bool:
        print("items")
        return False

    def __choices_flee(self) -> bool:
        # todo check chances of fleeing
        self.__end_of_fight_callback()
        return False

    def attack(self) -> bool:
        """

        :return: True if fight is over (attack was successful -> enemy is dead), False otherwise
        """
        if self.__enemy is None:
            Logger.instance().error("Error! Enemy is not set!")
            return False

        result = self.__player.measure()
        self.__stv_player.set_data(result)
        self.__stv_diff.set_data(result.get_diff(self.__enemy.get_statevector()))
        self.render()

        return self.__enemy.damage(result)


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

        file = open("D:\\" + os.path.join(folder, file_name), "x")
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
        #self.__refocus()
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
