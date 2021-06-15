
from py_cui.widgets import BlockLabel
from util.logger import Logger
from game.map.map import Map


class MapWidget:
    def __init__(self, map_widget: BlockLabel, logger: Logger):
        self.__map_widget = map_widget
        self.__logger = logger
        self.__map = None

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
