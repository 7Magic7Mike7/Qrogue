import math
from typing import List, Callable, Optional, Dict, Tuple, Iterable

from qrogue.game.world.dungeon_generator import QrogueLevelGenerator
from qrogue.game.world.dungeon_generator.dungeon_parser.QrogueDungeonParser import QrogueDungeonParser
from qrogue.game.world.map import rooms, LevelMap
from qrogue.game.world.map.rooms import AreaType
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import RandomManager, MyRandom, MapConfig

from qrogue.util.util_functions import enum_str


# todo subclassing QrogueLevelGenerator seems inefficient due to handling rooms and other stuff we don't need
class WFCLayoutLearner(QrogueLevelGenerator):
    def __init__(self, pos_weights: Dict[Coordinate, Dict[rooms.AreaType, int]],
                 type_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]],
                 connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]]):
        def trigger_event(_: str):
            pass

        def load_map_callback(_: str, __: Coordinate):
            pass

        def show_message_callback(_: str, __: str, ___: Optional[bool], ____: Optional[int]):
            pass
        # seed is not needed since we don't work with room content
        super().__init__(0, lambda _: False, trigger_event, load_map_callback, show_message_callback)

        self.__pos_weights: Dict[Coordinate, Dict[rooms.AreaType, int]] = pos_weights
        self.__type_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = type_weights
        self.__connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = \
            connection_weights

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[Optional[LevelMap], bool]:
        _, success = super(WFCLayoutLearner, self).generate(file_name, in_dungeon_folder)
        return None, success

    def visitLayout(self, ctx: QrogueDungeonParser.LayoutContext) -> List[List[rooms.Room]]:
        room_matrix = super(WFCLayoutLearner, self).visitLayout(ctx)

        def get_room_type(x_: int, y_: int) -> AreaType:
            if 0 <= y_ < len(room_matrix) and 0 <= x_ < len(room_matrix[y_]):
                if room_matrix[y_][x_] is None:
                    return AreaType.EmptyRoom
                else:
                    return room_matrix[y_][x_].type
            else:
                return AreaType.Invalid

        for y in range(len(room_matrix)):
            for x in range(len(room_matrix[y])):
                room = room_matrix[y][x]
                if room is None:
                    rtype = AreaType.EmptyRoom
                else:
                    rtype = room.type

                # init dicts if needed
                c = Coordinate(x, y)
                if c not in self.__pos_weights:
                    self.__pos_weights[c] = {}
                if rtype not in self.__type_weights:
                    self.__type_weights[rtype] = {}
                    self.__connection_weights[rtype] = {}
                cur_dict = self.__type_weights[rtype]

                # increase weight of this room's type for the current position
                if rtype in self.__pos_weights[c]:
                    self.__pos_weights[c][rtype] += 1
                else:
                    self.__pos_weights[c][rtype] = 1

                # find out the type of the room's neighbors
                neighbors: Dict[Direction, AreaType] = {}
                for val in Direction.values():
                    neighbors[val] = get_room_type(x + val.x, y + val.y)

                # update the weights accordingly
                for direction in neighbors:
                    ntype = neighbors[direction]
                    if ntype in cur_dict:
                        cur_dict[ntype] += 1
                    else:
                        cur_dict[ntype] = 1

                    # check for hallway
                    if room is not None and room.get_hallway(direction, throw_error=False) is not None:
                        if ntype in self.__connection_weights[rtype]:
                            self.__connection_weights[rtype][ntype] += 1
                        else:
                            self.__connection_weights[rtype][ntype] = 1

        return room_matrix


class WFCLayoutGenerator:
    class WaveFunction:
        def __init__(self, weights: Dict[Optional[rooms.AreaType], float]):
            self.__weights = weights
            self.__state: Optional[rooms.AreaType] = None

        @property
        def is_collapsed(self) -> bool:
            return self.__state is not None

        @property
        def state(self) -> rooms.AreaType:
            assert self.is_collapsed, "WaveFunction not yet collapsed!"
            return self.__state

        def adapt_weights(self, type_weights: Dict[Optional[rooms.AreaType], int]):
            if self.is_collapsed:
                return  # no need to adapt anything

            weight_sum = sum(type_weights.values())

            for key in self.__weights:
                if key in type_weights:
                    norm_weight = type_weights[key] / weight_sum
                    # for now the normalization will not be perfectly accurate
                    # todo fix/come up with solution (floats?)
                    self.__weights[key] = int(self.__weights[key] * (1 + norm_weight))    # e.g. increase weight by 20% = multiply by 1.2
                else:
                    self.__weights.pop(key)     # non-existing key is like a 0 weight, meaning we can simply remove it

            if len(self.__weights) == 0 and not self.is_collapsed:
                self.__state = AreaType.EmptyRoom   # collapse to empty room if no more AreaTypes are possible

        def collapse(self, rand: MyRandom) -> rooms.AreaType:
            if self.is_collapsed:
                return self.__state

            weight_sum = sum(self.__weights.values())
            rand_val = rand.get_int(0, weight_sum, "WaveFunction.collapse()")
            val = 0
            for key in self.__weights:
                weight = self.__weights[key]
                val += weight
                if rand_val < val:
                    self.__state = key
                    return self.__state
            return AreaType.Invalid     # this should not be possible to happen

        def force_spawn_room(self):
            assert not self.is_collapsed, "Forcing an already collapsed WaveFunction to be a SpawnRoom!"
            self.__state = AreaType.SpawnRoom

        def __str__(self):
            if self.is_collapsed:
                return f"WF ({self.__state})"
            else:
                text = f"WF (?"
                weight_sum = sum(self.__weights.values())
                for key in self.__weights:
                    text += f"{enum_str(key)} {(100 * self.__weights[key] / weight_sum):.0f}% | "
                text = text[:-2] + ")"
                return text

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
        wave_functions: Dict[Coordinate, WFCLayoutGenerator.WaveFunction] = {}
        positions = []
        for x in range(width):
            for y in range(height):
                c = Coordinate(x, y)
                positions.append(c)
                wave_functions[c] = WFCLayoutGenerator.WaveFunction(self.__pos_weights[c])

        entropies: Dict[Coordinate, float] = {}
        for pos in positions:
            entropies[pos] = self.__get_entropy(pos)

        # randomly place the SpawnRoom
        sr_pos = Coordinate(self.__rand.get_int(0, width), self.__rand.get_int(0, height))
        wave_functions[sr_pos].force_spawn_room()
        entropies.pop(sr_pos)

        while len(entropies) > 0:
            pos = self.min_entropy(entropies)
            rtype = wave_functions[pos].collapse(self.__rand)

            # propagate collapse to all neighbors
            for direction in Direction.values():
                neighbor_pos = pos + direction
                if 0 <= neighbor_pos.x < width and 0 <= neighbor_pos.y < height:
                    wave_functions[neighbor_pos].adapt_weights(self.__type_weights[rtype])

            entropies.pop(pos)  # the position no longer needs to be handled

        layout = [[AreaType.EmptyRoom] * width for _ in range(height)]
        for pos in wave_functions:
            layout[pos.y][pos.x] = wave_functions[pos].state

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
