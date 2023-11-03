import math
from typing import List, Optional, Dict, Tuple, Iterable, Any

from qrogue.game.world.dungeon_generator import QrogueLevelGenerator
from qrogue.game.world.dungeon_generator.path_search import Search
from qrogue.game.world.dungeon_generator.wave_function_collapse import WaveFunction, WFCLearner
from qrogue.game.world.dungeon_generator.wave_function_collapse.learnables import LearnableMap, WFCLearnMatrix, \
    LearnableRoom
from qrogue.game.world.map import rooms, LevelMap
from qrogue.game.world.map.rooms import AreaType
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import TileCode
from qrogue.util import RandomManager, MapConfig, MyRandom

from qrogue.util.util_functions import my_str


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

    def __init__(self, seed: int, data: Optional[List[WFCLearnMatrix]] = None):
        """
        Learns the wave function from the given templates and builds a level layout based on that.

        :param seed:
        """
        self.__rand = RandomManager.create_new(seed)
        self.__pos_weights: Dict[Coordinate, Dict[Any, int]] = {}
        self.__type_weights: Dict[Optional[Any], Dict[Optional[Any], int]] = {}
        self.__learner = WFCLearner(self.__pos_weights, self.__type_weights)

        self.__entropies: Dict[Coordinate, float] = {}
        self.__wave_functions: Dict[Coordinate, WaveFunction] = {}
        self.__width: Optional[int] = None
        self.__height: Optional[int] = None
        self.__data = []

        if data is not None:
            self.add_knowledge(data)

    @property
    def _rand(self) -> MyRandom:
        return self.__rand

    def add_knowledge(self, data: List[WFCLearnMatrix]):
        assert len(data) > 0, "Cannot learn from empty list!"

        for matrix in data:
            self.__learner.learn(matrix)
        self.__learner.remove_unwanted_values()
        self.__data += data

        width = min([val.width for val in data])
        if self.__width is None:
            self.__width = width
        else:
            self.__width = min(self.__width, width)
        height = min([val.height for val in data])
        if self.__height is None:
            self.__height = height
        else:
            self.__height = min(self.__height, height)

        for x in range(self.__width):
            for y in range(self.__height):
                c = Coordinate(x, y)
                self.__entropies[c] = self.__get_entropy(c)
                if c in self.__pos_weights:
                    self.__wave_functions[c] = WaveFunction(self.__pos_weights[c])
                else:
                    self.__wave_functions[c] = WaveFunction({})

    def __weight(self, main: Any, neighbor: Any) -> float:
        """

        :param main: type of the main room
        :param neighbor: type of potential neighbor
        :return: normalized weight for the corresponding types
        """
        if main not in self.__type_weights or neighbor not in self.__type_weights[main]:
            return 0
        return self.__type_weights[main][neighbor] / sum(self.__type_weights[main].values())

    def __weight_values(self, main: Any) -> Iterable[int]:
        if main not in self.__type_weights:
            return []
        return self.__type_weights[main].values()

    def __weight_sum(self, main: Any) -> int:
        if main not in self.__type_weights:
            return 0
        return sum(self.__type_weights[main].values())

    def __get_entropy(self, pos: Coordinate) -> float:
        if pos in self.__pos_weights:
            # shannon_entropy_for_square = log(sum(weight)) - (sum(weight * log(weight)) / sum(weight))
            weight_sum = sum(self.__pos_weights[pos].values())
            log_sum = 0
            for w in self.__pos_weights[pos].values():
                if w > 0:
                    log_sum += w * math.log(w)
            entropy = math.log(weight_sum) - (log_sum / weight_sum)
            return entropy
        return 0    # todo check which value to pick

    def generate(self, seed: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Any]] = None) -> List[List[Any]]:
        assert len(self.__data) > 0, "Cannot generate without learning from data before!"

        if seed is None:
            rand = self.__rand
        else:
            rand = RandomManager.create_new(seed)

        # if no dimensions are given we take the smallest one that fits all data
        if width is None:
            width = min([val.width for val in self.__data])
        if height is None:
            height = min([val.height for val in self.__data])

        # copy wave functions
        wave_functions: Dict[Coordinate, WaveFunction] = {}
        for pos in self.__wave_functions:
            wave_functions[pos] = self.__wave_functions[pos].copy()

        def propagate_collapse(position: Coordinate, collapsed_state: Any):
            # propagate collapse to all neighbors
            for direction in Direction.values():
                neighbor_pos = position + direction
                if 0 <= neighbor_pos.x < width and 0 <= neighbor_pos.y < height:
                    wave_functions[neighbor_pos].adapt_weights(self.__type_weights[collapsed_state])

        if static_entries is not None:
            for pos in static_entries:
                value = static_entries[pos]
                wave_functions[pos].force_value(value)
                propagate_collapse(pos, value)

        entropies = self.__entropies.copy()
        while len(entropies) > 0:
            pos = WFCGenerator.min_entropy(entropies)
            value = wave_functions[pos].collapse(rand)
            propagate_collapse(pos, value)
            entropies.pop(pos)  # the position no longer needs to be handled

        matrix = [[None] * width for _ in range(height)]
        for pos in wave_functions:
            matrix[pos.y][pos.x] = wave_functions[pos].state
        return matrix

    def to_string(self, values_of_interest: Iterable[Any]) -> str:
        text = "WFC probabilities by feature type {\n"
        for main in values_of_interest:
            text += f"\t{my_str(main)} ("
            for neighbor in values_of_interest:
                probability = self.__weight(main, neighbor)
                if probability > 0:
                    text += f"{my_str(neighbor)}: {probability * 100}%, "
            text += ")\n"
        text += "}"
        return text

    def __str__(self):
        return self.to_string(self.__type_weights)


def load_level(seed: int, file_name: str, in_dungeon_folder: bool) -> Optional[LevelMap]:
    generator = QrogueLevelGenerator(seed, lambda s: True, lambda s: None, lambda s, c: None, lambda s0, s1: None)
    level, _ = generator.generate(file_name, in_dungeon_folder)
    return level


class WFCLayoutGenerator(WFCGenerator):
    def __init__(self, seed: int, templates: List[Tuple[str, bool]]):
        """
        Learns the wave function from the given templates and builds a level layout based on that.

        :param seed:
        :param templates: list of tuples that define a filename and whether it can be found in the dungeon folder or not
        """
        self.__connection_weights: Dict[Optional[rooms.AreaType], Dict[Optional[rooms.AreaType], int]] = {}

        data: List[LearnableMap] = []
        for template in templates:
            # load levels
            filename, in_dungeon_folder = template
            level = load_level(seed, filename, in_dungeon_folder)
            assert level is not None, f"Could not learn from file \"{filename}\""

            data.append(LearnableMap(level))

        super(WFCLayoutGenerator, self).__init__(seed, data)

    def generate(self, seed: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Any]] = None) -> List[List[AreaType]]:
        # we need to first place a SpawnRoom as static entry
        if static_entries is None:
            static_entries = {}
        # todo random based on type_weights
        spawn_x = self._rand.get_int(0, MapConfig.map_width(), "spawn_x in WFCLayoutGenerator")
        spawn_y = self._rand.get_int(0, MapConfig.map_height(), "spawn_y in WFCLayoutGenerator")
        static_entries[Coordinate(spawn_x, spawn_y)] = AreaType.SpawnRoom

        return super(WFCLayoutGenerator, self).generate(seed, width, height, static_entries)


class WFCConnectionGenerator(WFCGenerator):
    # todo implement? but not needed if we use WFC just for the rooms and not the layout
    pass


class WFCRoomGenerator(WFCGenerator):
    @staticmethod
    def get_level_list() -> List[Tuple[str, bool]]:
        return [(level, True) for level in MapConfig.level_list()]

    def __init__(self, seed: int, templates: List[Tuple[str, bool]], room_type: rooms.AreaType):
        self.__room_type = room_type

        data: List[LearnableRoom] = []
        for template in templates:
            # load levels
            filename, in_dungeon_folder = template
            level = load_level(seed, filename, in_dungeon_folder)
            assert level is not None, f"Could not learn from file \"{filename}\""

            # load rooms from the provided levels
            for x in range(level.width):
                for y in range(level.height):
                    room = level.room_at(x, y)
                    if room is not None and room.type == room_type:
                        data.append(LearnableRoom(room))

        super(WFCRoomGenerator, self).__init__(seed, data)

    @property
    def room_type(self) -> rooms.AreaType:
        return self.__room_type

    def generate(self, seed: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Any]] = None) -> List[List[Any]]:
        # generate tile matrix
        matrix: List[List[LearnableRoom.TileData]] = super(WFCRoomGenerator, self).generate(seed, width, height, static_entries)

        # adapt matrix such that every Collectible can be picked up and every Enemy can be fought
        entrances: List[Coordinate] = [
            Coordinate(rooms.Room.INNER_MID_X, 0),  # North entrance
            Coordinate(0, rooms.Room.INNER_MID_Y),  # West entrance
            Coordinate(rooms.Room.INNER_WIDTH-1, rooms.Room.INNER_MID_Y),   # East entrance
            Coordinate(rooms.Room.INNER_MID_X, rooms.Room.INNER_HEIGHT-1),  # South entrance
        ]

        interactable_tiles: List[Coordinate] = []
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                tile_data = matrix[row][col]
                if tile_data.code in [TileCode.Enemy, TileCode.Collectible]:    # find all enemies and collectibles
                    interactable_tiles.append(Coordinate(col, row))
        # todo filter interactable_tiles such that only unobtainable tiles are left


        # make every interactable tile accessible from an entrance
        for pos in interactable_tiles:
            weight_matrix = Search.get_weighted_obstacles_matrix(pos, get_tile_code=lambda c: matrix[c.y][c.x].code)
            path = Search.simple_room_visit(pos, get_weight=lambda c: weight_matrix[c.y][c.x],
                                            is_goal=lambda c: c in entrances)
            # replace all obstacles and walls on the path with floors to make them accessible
            for co in path:
                if matrix[co.y][co.x].code in [TileCode.Obstacle, TileCode.Wall]:
                    matrix[co.y][co.x] = LearnableRoom.TileData(TileCode.Floor, None)     # Floor tiles don't have data

        return matrix
