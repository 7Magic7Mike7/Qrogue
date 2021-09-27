from abc import ABC, abstractmethod

from py_cui.widgets import BlockLabel

import game.map.tiles as tiles
from game.logic.instruction import HGate
from game.logic.qubit import StateVector
from game.map.map import Map
from util.logger import Logger
from widgets.renderer import TileRenderer


class Widget(ABC):
    def __init__(self, widget: BlockLabel):
        self.__widget = widget

    @property
    def widget(self):
        return self.__widget

    @abstractmethod
    def set_data(self, data):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def render_reset(self):
        pass


class CircuitWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__player = None

    def set_data(self, player: tiles.Player):
        self.__player = player.player

    def render(self):
        if self.__player is not None:
            circ_str = ""       # todo prepend generator!
            instructions = self.__player.instructions
            if len(instructions) > 0:
                rows = ["|" + HGate(0).abbreviation(0) + "|---"] * self.__player.num_of_qubits
                for inst in instructions:
                    used_qubits = [False] * self.__player.num_of_qubits
                    max_len = 0
                    for q in inst.qargs:
                        used_qubits[q] = True
                        inst_str = f"--<{inst.abbreviation(q)}>--"
                        max_len = max(max_len, len(inst_str))
                        rows[q] += inst_str
                    for i in range(len(used_qubits)):
                        if not used_qubits[i]:
                            rows[i] += ("-" * max_len)
            else:
                rows = ["-------"] * self.__player.num_of_qubits
            for row in rows:
                circ_str += row + "\n"
            self.widget.set_title(circ_str)

    def render_reset(self):
        self.widget.set_title("")


class EventInfoWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__enemy = None

    def set_data(self, enemy: tiles.Enemy):
        self.__enemy = enemy

    def render(self):
        if self.__enemy is not None:
            self.widget.set_title(self.__enemy.__str__())

    def render_reset(self):
        self.widget.set_title("")


class EventQubitsWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__enemy = None

    def set_data(self, enemy: tiles.Enemy):  # todo change name from enemy to event?
        self.__enemy = enemy

    def render(self):
        if self.__enemy is not None:
            sb = ""
            for q in self.__enemy.target:
                sb += f"{q}\n"
            self.widget.set_title(sb)

    def render_reset(self):
        self.widget.set_title("")


class PlayerInfoWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__player = None
        self.__selection = 0

    @property
    def circuit(self):
        return self.__selection

    def set_data(self, player: tiles.Player):
        self.__player = player.player

    def prev(self):
        self.__selection = self.__selection - 1
        if self.__selection < 0:
            self.__selection = self.__player.backpack.size

    def next(self):
        self.__selection = self.__selection + 1
        if self.__selection >= self.__player.backpack.size + 2: # +0... Remove, +1... Wait
            self.__selection = 0

    def render(self):
        if self.__player is not None:
            sb = ""
            for i in range(self.__player.backpack.size + 2):
                if i == self.__selection:
                    sb += "x "  # todo: use color instead?
                if i >= self.__player.backpack.size:
                    action = i - self.__player.backpack.size
                    if action == 0:
                        sb += "Remove"
                    else:
                        sb += "Wait"
                else:
                    sb += self.__player.backpack.get(i).__str__()
                sb += "\n"
            self.widget.set_title(sb)


    def render_reset(self):
        self.widget.set_title("")


class PlayerQubitsWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__player = None

    def set_data(self, player: tiles.Player):
        self.__player = player.player

    def render(self):
        if self.__player is not None:
            sb = ""
            for i in range(self.__player.num_of_qubits):
                sb += self.__player.get_qubit_string(i)
                sb += "\n"
            self.widget.set_title(sb)

    def render_reset(self):
        self.widget.set_title("")


class MapWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__map = None
        self.__backup = None

    def set_data(self, map: Map):
        self.__map = map

    def render(self):   # todo more efficient rendering!
        if self.__map is not None:
            str_rep = ""
            for y in range(self.__map.height):
                for x in range(self.__map.width):
                    tile = self.__map.at(x, y)
                    str_rep += TileRenderer.instance().render(tile)
                str_rep += "\n"
            self.widget.set_title(str_rep)

    def render_reset(self):
        self.__backup = self.widget.get_title().title()
        self.widget.set_title("")


def init_color_rules(map_widget: MapWidget):
    map_widget.widget.add_text_color_rule('P', tiles.get_color(tiles.TileCode.Player), 'contains', match_type='regex')
    map_widget.widget.add_text_color_rule('B', tiles.get_color(tiles.TileCode.Boss), 'contains', match_type='regex')
    map_widget.widget.add_text_color_rule('\d', tiles.get_color(tiles.TileCode.Enemy), 'contains', match_type='regex')
    map_widget.widget.add_text_color_rule('#', tiles.get_color(tiles.TileCode.Wall), 'contains', match_type='regex')


class StateVectorWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__state_vector = None

    def set_data(self, state_vector: StateVector):
        self.__state_vector = state_vector

    def render(self):
        if self.__state_vector is not None:
            str_rep = "__"
            str_rep += str(self.__state_vector)
            self.widget.set_title(str_rep)

    def render_reset(self):
        self.widget.set_title("")
