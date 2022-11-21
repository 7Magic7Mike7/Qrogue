import math
from typing import List, Optional, Dict, Tuple, Iterable

from qrogue.game.world.dungeon_generator.wave_function_collapse import WaveFunction, WFCLayoutLearner
from qrogue.game.world.map import rooms
from qrogue.game.world.map.rooms import AreaType
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import RandomManager, MapConfig

from qrogue.util.util_functions import enum_str


class WFCGenerator:
    @staticmethod
    def min_entropy(entropies: Dict[Coordinate, float]) -> Coordinate:
        min_pos = None
        min_val = -1
        for pos in entropies:
            val = entropies[pos]
            if min_val == -1 or val < min_val:
                min_pos = pos
                min_val = val
        return min_pos

    def __init__(self):
        pass


class WFCLayoutGenerator:
    def __init__(self, seed: int, templates: List[Tuple[str, bool]]):
        """
        Learns the wave function from the given templates and builds a level layout based on that.

        :param seed:
        :param templates: list of tuples that define a filename and whether it can be found in the dungeon folder or not
        """
        self.__rand = RandomManager.create_new(seed)
        self.__pos_weights: Dict[Coordinate, Dict[rooms.AreaType, int]] = {}
        self.__type_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = {}
        self.__connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = {}

        for template in templates:
            filename, in_dungeon_folder = template
            learner = WFCLayoutLearner(self.__pos_weights, self.__type_weights, self.__connection_weights)
            _, success = learner.generate(filename, in_dungeon_folder)
            assert success, f"Could not learn from file \"{filename}\""

    def __weight(self, rtype: AreaType, ntype: AreaType) -> float:
        """

        :param rtype: type of the main room
        :param ntype: type of a potential neighbor
        :return: normalized weight for the corresponding types
        """
        if rtype not in self.__type_weights or ntype not in self.__type_weights[rtype]:
            return 0
        return self.__type_weights[rtype][ntype] / sum(self.__type_weights[rtype].values())

    def __weight_values(self, rtype: AreaType) -> Iterable:
        if rtype not in self.__type_weights:
            return []
        return self.__type_weights[rtype].values()

    def __weight_sum(self, rtype: AreaType) -> int:
        if rtype not in self.__type_weights:
            return 0
        return sum(self.__type_weights[rtype].values())

    def __get_entropy(self, pos: Coordinate) -> float:
        # todo check for boundaries
        # shannon_entropy_for_square = log(sum(weight)) - (sum(weight * log(weight)) / sum(weight))
        weight_sum = sum(self.__pos_weights[pos].values())
        entropy = math.log(weight_sum) - (sum([w * math.log(w) for w in self.__pos_weights[pos].values()]) / weight_sum)
        return entropy

    def generate(self, seed: Optional[int] = None):
        if seed is None:
            rand = self.__rand
        else:
            rand = RandomManager.create_new(seed)

        width, height = MapConfig.map_width(), MapConfig.map_height()
        wave_functions: Dict[Coordinate, WaveFunction] = {}
        positions = []
        for x in range(width):
            for y in range(height):
                c = Coordinate(x, y)
                positions.append(c)
                wave_functions[c] = WaveFunction(self.__pos_weights[c])

        entropies: Dict[Coordinate, float] = {}
        for pos in positions:
            entropies[pos] = self.__get_entropy(pos)

        # randomly place the SpawnRoom
        sr_pos = Coordinate(rand.get_int(0, width), rand.get_int(0, height))
        wave_functions[sr_pos].force_value(AreaType.SpawnRoom)
        entropies.pop(sr_pos)

        while len(entropies) > 0:
            pos = WFCGenerator.min_entropy(entropies)
            rtype = wave_functions[pos].collapse(rand)

            # propagate collapse to all neighbors
            for direction in Direction.values():
                neighbor_pos = pos + direction
                if 0 <= neighbor_pos.x < width and 0 <= neighbor_pos.y < height:
                    wave_functions[neighbor_pos].adapt_weights(self.__type_weights[rtype])

            entropies.pop(pos)  # the position no longer needs to be handled

        layout = [[AreaType.EmptyRoom] * width for _ in range(height)]
        for pos in wave_functions:
            layout[pos.y][pos.x] = wave_functions[pos].state

    def __str__(self):
        text = "WFC probabilities by AreaType {\n"
        for rtype in AreaType.values(include_pseudo_areas=True, only_rooms=True):
            text += f"\t{enum_str(rtype)} ("
            for ntype in AreaType.values(include_pseudo_areas=True, only_rooms=True):
                probability = self.__weight(rtype, ntype)
                if probability > 0:
                    text += f"{enum_str(ntype)}: {probability * 100}%, "
            text += ")\n"
        text += "}"
        return text
