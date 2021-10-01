from abc import abstractmethod

import py_cui
from py_cui.widget_set import WidgetSet

from game.actors.enemy import Enemy
from game.map.map import Map
from game.map.tiles import Player as PlayerTile
from util.logger import Logger
from widgets.color_rules import ColorRules
from widgets.my_widgets import SelectionWidget, StateVectorWidget, CircuitWidget, MapWidget


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
        self.__map_widget = MapWidget(map_widget)

        ColorRules.apply_map_rules(self.__map_widget)

    def activate_logger(self):
        Logger.instance().set_label(self.__first_row)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__map_widget.widget

    def set_data(self, map: Map, player_tile: PlayerTile):
        self.__map = map
        self.__player_tile = player_tile
        self.__map_widget.set_data(map)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__map_widget
        ]

    def reset(self):
        self.__map_widget.widget.set_title("")


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


