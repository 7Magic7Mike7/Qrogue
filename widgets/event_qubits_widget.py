
from py_cui.widgets import BlockLabel
from game.actors.enemy import Enemy
from util.logger import Logger


class EventQubitsWidget:
    def __init__(self, event_qubits_widget: BlockLabel, logger: Logger):
        self.__widget = event_qubits_widget
        self.__logger = logger
        self.__enemy = None

    def set_enemy(self, enemy: Enemy):  # todo change name from enemy to event?
        self.__enemy = enemy

    def render(self):
        if self.__enemy is not None:
            sb = ""
            for i in range(self.__enemy.num_of_qubits):
                sb += self.__enemy.get_qubit_string(i)
                sb += "\n"  # todo use system newline
            self.__widget.set_title(sb)