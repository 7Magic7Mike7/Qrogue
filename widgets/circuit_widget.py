
from py_cui.widgets import BlockLabel

from game.actors.player import Player
from util.logger import Logger


class CircuitWidget:

    def __init__(self, circuit_widget: BlockLabel, logger: Logger):
        self.__widget = circuit_widget
        self.__logger = logger
        self.__player = None

    def set_player(self, player: Player):
        self.__player = player

    def render(self):
        if self.__player is not None:
            self.__widget.set_title(self.__player.circuit.__str__())