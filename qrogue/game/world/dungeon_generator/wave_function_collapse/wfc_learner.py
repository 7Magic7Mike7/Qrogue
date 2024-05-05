from typing import Any, Dict, Optional, List

from qrogue.game.world.dungeon_generator.wave_function_collapse import WFCLearnMatrix
from qrogue.game.world.dungeon_generator.wave_function_collapse.learnables import LearnableRoom
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import tiles


class WFCLearner:
    def __init__(self, pos_weights: Dict[Coordinate, Dict[Any, int]],
                 type_weights: Dict[Optional[Any], Dict[Any, int]]):
        self.__pos_weights = pos_weights
        self.__type_weights = type_weights

    def learn(self, matrix: WFCLearnMatrix):
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
