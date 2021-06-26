
from py_cui.widgets import BlockLabel
from game.actors.player import Player
from util.logger import Logger


class PlayerQubitsWidget:
    def __init__(self, player_qubits_widget: BlockLabel, logger: Logger):
        self.__widget = player_qubits_widget
        self.__logger = logger
        self.__player = None

    def set_player(self, player: Player):
        self.__player = player

    def render(self):
        if self.__player is not None:
            sb = ""
            for i in range(self.__player.num_of_qubits):
                sb += self.__player.get_qubit_string(i)
                sb += "\n"  # todo use system newline
            self.__widget.set_title(sb)
