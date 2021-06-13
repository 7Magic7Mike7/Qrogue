
from py_cui.widgets import BlockLabel
from util.logger import Logger


class Map:
    def __init__(self, map: BlockLabel, logger: Logger):
        self.__map = map
        self.__logger = logger
        logger.println("map created!")

    def move(self, direction):
        self.__logger.print(f"Moving in direction {direction}")