from abc import abstractmethod

import py_cui
from py_cui.widget_set import WidgetSet

from game.actors.enemy import Enemy
from game.controls import Controls
from game.map.navigation import Direction
from game.map.tiles import Player as PlayerTile
from util.logger import Logger
from widgets.my_widgets import *


class QrogueCUI(py_cui.PyCUI):
    def __init__(self, seed: int, controls: Controls, end_of_fight_callback, width: int = 8, height: int = 9):
        super().__init__(width, height)
        self.__map = None
        self.__seed = seed
        self.__controls = controls

        self.__explore = ExploreWidgetSet(Logger.instance())
        self.__fight = FightWidgetSet(Logger.instance(), end_of_fight_callback)

        self.__cur_widget_set = self.__explore
        self.__init_keys()

    def __init_keys(self):
        self.__explore.add_key_command(self.__controls.move_up, self.__move_up)
        self.__explore.add_key_command(self.__controls.move_right, self.__move_right)
        self.__explore.add_key_command(self.__controls.move_down, self.__move_down)
        self.__explore.add_key_command(self.__controls.move_left, self.__move_left)

        self.__fight.add_key_command(self.__controls.selection_up, self.__fight.selection_up)
        self.__fight.add_key_command(self.__controls.selection_right, self.__fight.selection_right)
        self.__fight.add_key_command(self.__controls.selection_down, self.__fight.selection_down)
        self.__fight.add_key_command(self.__controls.selection_left, self.__fight.selection_left)
        self.__fight.add_key_command(self.__controls.action, self.__fight.attack)

    def __refocus(self):
        # apparently we have to manually set and reset the focus for keys to work
        self.move_focus(self.__cur_widget_set.get_main_widget(), auto_press_buttons=False)
        self.lose_focus()

    def switch_to_explore(self, map: Map, player_tile: PlayerTile):
        self.__map = map
        self.__explore.set_data(map, player_tile)
        self.apply_widget_set(self.__explore)
        self.__refocus()

    def switch_to_fight(self, player_tile: PlayerTile, enemy: Enemy):
        enemy.fight_init(player_tile.player)
        self.__fight.set_data(player_tile, enemy)
        self.apply_widget_set(self.__fight)
        self.__refocus()

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
    def get_widget_list(self) -> "list of Widgets":
        pass

    @abstractmethod
    def get_main_widget(self) -> py_cui.widgets.Widget:
        pass


class ExploreWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 8
    __NUM_OF_COLS = 9

    def __init__(self, logger):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__map = None
        self.__player_tile = None
        first_row = self.add_block_label('first line (metadata like playtime, floor, ...?)', 0, 0,
                                         column_span=self.__NUM_OF_COLS)
        first_row.toggle_border()
        Logger.instance().set_label(first_row)

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

        init_color_rules(self.__main_widget)

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
        Logger.instance().println()
        return [
            self.__main_widget,
            self.__bottom_widget,
            self.__left_widget,
            self.__left_bottom_widget
        ]


class FightWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 6
    __NUM_OF_COLS = 3

    def __init__(self, logger, end_of_fight_callback):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__player = None
        self.__enemy = None
        self.__end_of_fight_callback = end_of_fight_callback

    def init_widgets(self):
        logger_row = self.add_block_label('Logger', 0, 0, row_span=1, column_span=self.__NUM_OF_COLS, center=True)
        logger_row.toggle_border()
        Logger.instance().set_label(logger_row)

        stv_row = 1
        stv = self.add_block_label('Player StV', stv_row, 0, row_span=3, column_span=1, center=True)
        self.__stv_player = StateVectorWidget(stv)
        stv = self.add_block_label('Diff StV', stv_row, 1, row_span=3, column_span=1, center=True)
        self.__stv_diff = StateVectorWidget(stv)
        stv = self.add_block_label('Enemy StV', stv_row, 2, row_span=3, column_span=1, center=True)
        self.__stv_enemy = StateVectorWidget(stv)

        circuit = self.add_block_label('Circuit', 4, 0, row_span=1, column_span=3, center=True)
        circuit.toggle_border()
        self.__circuit = CircuitWidget(circuit)

        choices = self.add_block_label('Choices', 5, 0, row_span=1, column_span=1, center=True)
        choices.toggle_border()
        self.__choices = PlayerInfoWidget(choices)
        details = self.add_block_label('Details', 5, 1, row_span=1, column_span=2, center=True)
        details.toggle_border()
        self.__details = PlayerInfoWidget(details)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__choices.widget

    def set_data(self, player_tile: PlayerTile, enemy: Enemy):
        self.__player = player_tile.player
        self.__enemy = enemy

        self.__circuit.set_data(player_tile)
        self.__choices.set_data(player_tile)
        self.__details.set_data(player_tile)

        self.__stv_player.set_data(player_tile.player.state_vector)
        self.__stv_enemy.set_data(enemy.get_statevector())

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__stv_player,
            self.__stv_diff,
            self.__stv_enemy,
            self.__circuit,
            self.__choices,
            self.__details
        ]

    def selection_up(self):
        self.__choices.prev()
        self.render()

    def selection_right(self):
        Logger.instance().clear()

    def selection_down(self):
        self.__choices.next()
        self.render()

    def selection_left(self):
        Logger.instance().clear()

    def attack(self):
        if self.__enemy is None:
            Logger.instance().print("Error! Enemy is not set!")
            return

        index = self.__details.circuit
        Logger.instance().println(f"Index = {index}", clear=True)
        if index >= self.__player.backpack.size:
            action = index - self.__player.backpack.size
            if action == 0:
                self.__player.remove_instruction(0)
            else:
                print("wait")
        else:
            self.__player.use_instruction(self.__details.circuit)
        result = self.__player.measure()
        Logger.instance().print(str(result))
        self.__enemy.damage(result) # todo this returns true if it damages the enemy -> therefore it kills the enemy
        if self.__enemy.is_alive():
            self.render()
        else:
            self.__end_of_fight_callback()
