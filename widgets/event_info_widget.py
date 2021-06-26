
from py_cui.widgets import BlockLabel
from game.actors.enemy import Enemy
from util.logger import Logger


class EventInfoWidget:
    def __init__(self, event_info_widget: BlockLabel, logger: Logger):
        self.__widget = event_info_widget
        self.__logger = logger
        self.__enemy = None

    def set_enemy(self, enemy: Enemy):
        self.__enemy = enemy

    def render(self):
        if self.__enemy is not None:
            self.__widget.set_title(self.__enemy.__str__())
