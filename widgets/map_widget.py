
from py_cui.widgets import BlockLabel
from util.logger import Logger
from game.map.map import Map
from game.map.navigation import Direction


class MapWidget:
    def __init__(self, map_widget: BlockLabel, logger: Logger):
        self.__map_widget = map_widget
        self.__logger = logger
        self.__map = None
        logger.println("map created!")

    def move(self, direction: Direction):
        self.__logger.println(f"Moving in direction {direction}")
        if self.__map is not None:
            if self.__map.move(direction):
                self.render()
            else:
                self.__logger.println(f"moving ({direction.name}) failed")

    def set_map(self, map: Map):
        self.__map = map

    def render(self):
        str_repr = map_to_string(self.__map)
        self.__map_widget.set_title(str_repr)


def map_to_string(map: Map):
    repr = ""
    for y in range(map.height()):
        for x in range(map.width()):
            val = map.at(x, y)
            repr += val.img
        repr += '\n'    # todo change to new line from system?
    return repr
