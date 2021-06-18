from py_cui.widgets import BlockLabel

from game.actors.player import Player
from util.logger import Logger


class PlayerInfoWidget:

    def __init__(self, player_info_widget: BlockLabel, logger: Logger):
        self.__widget = player_info_widget
        self.__logger = logger
        self.__player = None
        self.__circuit_selection = 0

    @property
    def circuit(self):
        return self.__circuit_selection

    def set_player(self, player: Player):
        self.__player = player

    def prev(self):
        self.__circuit_selection = self.__circuit_selection - 1
        if self.__circuit_selection < 0:
            self.__circuit_selection = self.__player.backpack.size - 1

    def next(self):
        self.__circuit_selection = self.__circuit_selection + 1
        if self.__circuit_selection >= self.__player.backpack.size:
            self.__circuit_selection = 0

    def render(self):
        if self.__player is not None:
            sb = ""
            for i in range(self.__player.backpack.size):
                if i == self.__circuit_selection:
                    sb += "x "  # todo: use color instead?
                sb += self.__player.backpack.get(i).__str__()
                sb += "\n"  # todo use system newline
            self.__widget.set_title(sb)
