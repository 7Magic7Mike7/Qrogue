from typing import Any, Dict, Optional, List, Iterator

from qrogue.game.world.dungeon_generator.wave_function_collapse import WFCLearnMatrix
from qrogue.game.world.navigation import Coordinate, Direction


class WFCLearner:
    def __init__(self, pos_weights: Dict[Coordinate, Dict[Any, int]],
                 type_weights: Dict[Optional[Any], Dict[Any, int]]):
        self.__pos_weights = pos_weights
        self.__type_weights = type_weights

        self.__width = -1
        self.__height = -1
        for coor in self.__pos_weights:
            if coor.x > self.__width:
                self.__width = coor.x
            if coor.y > self.__height:
                self.__height = coor.y

        # increment width and height since coordinates start at 0
        self.__width += 1
        self.__height += 1
        # if pos_weights was empty, width and height are now 0

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def positions(self) -> Iterator[Coordinate]:
        return iter(self.__pos_weights.keys())

    @property
    def types(self) -> Iterator[Optional[Any]]:
        return iter(self.__type_weights.keys())

    def pos_weights(self, pos: Coordinate) -> Dict[Any, int]:
        if pos in self.__pos_weights:
            return self.__pos_weights[pos].copy()
        return {}

    def type_weights(self, type_: Optional[Any]):
        if type_ in self.__type_weights:
            return self.__type_weights[type_].copy()
        return {}

    def learn(self, matrix: WFCLearnMatrix):
        if self.__width > 0:
            if matrix.width != self.__width:
                from qrogue.util import Config
                Config.check_reachability("WFCLearner.learn() inequal width")
                # todo: Log error?
        else:
            self.__width = matrix.width

        if self.__height > 0:
            if matrix.height != self.__height:
                from qrogue.util import Config
                Config.check_reachability("WFCLearner.learn() inequal height")
                # todo: Log error?
        else:
            self.__height = matrix.height

        for x in range(matrix.width):
            for y in range(matrix.height):
                value = matrix.at(x, y)

                # update positional weights
                c = Coordinate(x, y)
                if c not in self.__pos_weights:
                    self.__pos_weights[c] = {}
                if value not in self.__pos_weights[c]:
                    self.__pos_weights[c][value] = 0
                self.__pos_weights[c][value] += 1

                # update type weights
                if value not in self.__type_weights:
                    self.__type_weights[value] = {}
                neighbors = [matrix.at(x + direction.x, y + direction.y)
                             for direction in Direction.values()]
                for neigh in neighbors:
                    if neigh not in self.__type_weights[value]:
                        self.__type_weights[value][neigh] = 0
                    self.__type_weights[value][neigh] += 1

    def remove_unwanted_values(self) -> None:
        """
        Can be overwritten to define values that we don't want to learn from.

        :return: None
        """
        pass

    def _remove_unwanted_values(self, values: List[Any]):
        """
        Can be used by subclasses to easily remove the listed values from the learned weights

        :param values:
        :return:
        """
        for pos in self.__pos_weights:
            for tc in self.__pos_weights[pos]:
                if tc in values:
                    # by setting count to 0 we "delete" it without messing up the loop
                    self.__pos_weights[pos][tc] = 0

        for tc in values:
            if tc in self.__type_weights:
                self.__type_weights.pop(tc)
