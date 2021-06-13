
from py_cui.widgets import BlockLabel
from util.logger import Logger


class MapWidget:
    def __init__(self, map_widget: BlockLabel, logger: Logger):
        self.__map_widget = map_widget
        self.__logger = logger
        logger.println("map created!")

    def move(self, direction):
        self.__logger.print(f"Moving in direction {direction}")