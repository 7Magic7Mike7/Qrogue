import json
import math
from typing import List, Optional, Dict, Tuple, Iterable, Any, Callable

from qrogue.game.world.dungeon_generator import QrogueLevelGenerator
from qrogue.game.world.map import LessonMap, CallbackPack
from qrogue.game.world.map.rooms import AreaType
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import TileCode, Tile
from qrogue.util import RandomManager, MapConfig, MyRandom, Logger
from qrogue.util.util_functions import my_str
from .learnables import LearnableMap, LearnableRoom
from .wave_function import WaveFunction
from .wfc_learner import WFCLearner, WFCLearnMatrix


class WFCGenerator:
    @staticmethod
    def get_pos_weight_json_string(wfc_gen: "WFCGenerator") -> str:
        json_dicts = []
        for pos in wfc_gen.__learner.positions:
            json_dict = {}
            for key, value in wfc_gen.__learner.pos_weights(pos).items():
                json_dict[my_str(key)] = my_str(value)
            json_str = json.dumps(json_dict)
            json_dicts.append(f"\t\"{my_str(pos)}\": {json_str}")
        return "{\n" + ", \n".join(json_dicts) + "\n}"

    @staticmethod
    def get_type_weight_json_string(wfc_gen: "WFCGenerator") -> str:
        json_dicts = []
        for type_ in wfc_gen.__learner.types:
            json_dict = {}
            for key, value in wfc_gen.__learner.type_weights(type_).items():
                json_dict[my_str(key)] = my_str(value)
            json_str = json.dumps(json_dict)
            json_dicts.append(f"\t\"{my_str(type_)}\": {json_str}")
        return "{\n" + ", \n".join(json_dicts) + "\n}"

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

    def __init__(self, pos_weights: Optional[Dict[Coordinate, Dict[Any, int]]] = None,
                 type_weights: Optional[Dict[Optional[Any], Dict[Any, int]]] = None,
                 data: Optional[List[WFCLearnMatrix]] = None):
        """
        Learns a wave function from the given data.
        """
        if pos_weights is None: pos_weights = {}
        if type_weights is None: type_weights = {}
        self.__learner = WFCLearner(pos_weights, type_weights)

        if data is not None:
            self.add_knowledge(data)

    def add_knowledge(self, data: List[WFCLearnMatrix]):
        assert len(data) > 0, "Cannot learn from empty list!"

        for matrix in data:
            self.__learner.learn(matrix)    # this updates pos_weights and type_weights
        self.__learner.remove_unwanted_values()

    def __weight(self, main: Any, neighbor: Any) -> float:
        """

        :param main: type of the main room
        :param neighbor: type of potential neighbor
        :return: normalized weight for the corresponding types
        """
        if main not in self.__learner.types or neighbor not in self.__learner.type_weights(main):
            return 0
        return self.__learner.type_weights(main)[neighbor] / sum(self.__learner.type_weights(main).values())

    def __weight_values(self, main: Any) -> Iterable[int]:
        if main not in self.__learner.types:
            return []
        return self.__learner.type_weights(main).values()

    def __weight_sum(self, main: Any) -> int:
        if main not in self.__learner.types:
            return 0
        return sum(self.__learner.type_weights(main).values())

    def __get_entropy(self, pos: Coordinate) -> float:
        if pos in self.__learner.positions:
            # shannon_entropy_for_square = log(sum(weight)) - (sum(weight * log(weight)) / sum(weight))
            weight_sum = sum(self.__learner.pos_weights(pos).values())
            log_sum = 0
            for w in self.__learner.pos_weights(pos).values():
                if w > 0:
                    log_sum += w * math.log(w)
            entropy = math.log(weight_sum) - (log_sum / weight_sum)
            return entropy
        return 0  # todo check which value to pick

    def generate(self, seed: int, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Any]] = None,
                 is_assignable: Optional[Callable[[Any, Any], bool]] = None) -> List[List[Any]]:
        assert self.__learner.width > 0 and self.__learner.height > 0, \
            "Cannot generate without learning from data before!"

        rand: MyRandom = RandomManager.create_new(seed)

        # if no dimensions are given we take the learned one
        if width is None: width = self.__learner.width
        if height is None: height = self.__learner.height

        # create wave functions
        wave_functions: Dict[Coordinate, WaveFunction] = {}
        entropies: Dict[Coordinate, float] = {}
        for x in range(self.__learner.width):
            for y in range(self.__learner.height):
                c = Coordinate(x, y)
                entropies[c] = self.__get_entropy(c)
                if c in self.__learner.positions:
                    wave_functions[c] = WaveFunction(self.__learner.pos_weights(c))
                else:
                    wave_functions[c] = WaveFunction({})

        def propagate_collapse(position: Coordinate, collapsed_state: Any):
            # propagate collapse to all neighbors
            for direction in Direction.values():
                neighbor_pos = position + direction
                if 0 <= neighbor_pos.x < width and 0 <= neighbor_pos.y < height:
                    wave_functions[neighbor_pos].adapt_weights(self.__learner.type_weights(collapsed_state))

        if static_entries is not None:
            for pos in static_entries:
                value = static_entries[pos]
                if wave_functions[pos].force_value(value, is_assignable):
                    propagate_collapse(pos, wave_functions[pos].state)
                else:
                    Logger.instance().error(f"Failed to force value={value} for static entry at {pos}", show=False,
                                            from_pycui=False)

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
            neighbor_texts = []
            for neighbor in values_of_interest:
                probability = self.__weight(main, neighbor)
                if probability > 0:
                    neighbor_texts.append(f"{my_str(neighbor)}: {probability * 100:2f}%")
            text += ", ".join(neighbor_texts)
            text += ")\n"
        text += "}"
        return text

    def __str__(self):
        return self.to_string(self.__learner.types)


def load_level(file_name: str, in_dungeon_folder: bool) -> Optional[LessonMap]:
    static_seed = 7  # seed does not matter since we are only interested in learning placements
    generator = QrogueLevelGenerator(lambda s: True, lambda s: None, lambda s, c: None, lambda s0, s1: None,
                                     CallbackPack.dummy())
    level, _ = generator.generate(static_seed, file_name, in_dungeon_folder)
    return level


class WFCLayoutGenerator(WFCGenerator):
    def __init__(self, templates: List[Tuple[str, bool]]):
        """
        Learns the wave function from the given templates and builds a level layout based on that.

        :param templates: list of tuples that define a filename and whether it can be found in the dungeon folder or not
        """
        self.__connection_weights: Dict[Optional[AreaType], Dict[Optional[AreaType], int]] = {}

        data: List[LearnableMap] = []
        for template in templates:
            # load levels
            filename, in_dungeon_folder = template
            level = load_level(filename, in_dungeon_folder)
            assert level is not None, f"Could not learn from file \"{filename}\""

            data.append(LearnableMap(level))

        super(WFCLayoutGenerator, self).__init__(data=data)

    def generate(self, seed: int, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, AreaType]] = None,
                 is_assignable: Optional[Callable[[AreaType, AreaType], bool]] = None) -> List[List[AreaType]]:
        # we need to first place a SpawnRoom as static entry
        if static_entries is None:
            static_entries = {}
        rm = RandomManager.create_new(seed)
        # todo random based on type_weights
        spawn_x = rm.get_int(0, MapConfig.map_width(), "spawn_x in WFCLayoutGenerator")
        spawn_y = rm.get_int(0, MapConfig.map_height(), "spawn_y in WFCLayoutGenerator")
        static_entries[Coordinate(spawn_x, spawn_y)] = AreaType.SpawnRoom

        return super(WFCLayoutGenerator, self).generate(seed, width, height, static_entries, is_assignable)


class WFCRoomGenerator(WFCGenerator):
    @staticmethod
    def get_level_list() -> List[Tuple[str, bool]]:
        return [(level, True) for level in MapConfig.level_list()[2:]]

    @staticmethod
    def from_level_files(templates: List[Tuple[str, bool]], room_type: AreaType) -> "WFCRoomGenerator":
        data: List[LearnableRoom] = []
        for template in templates:
            # load levels
            filename, in_dungeon_folder = template
            level = load_level(filename, in_dungeon_folder)
            assert level is not None, f"Could not learn from file \"{filename}\""

            # load rooms from the provided levels
            for x in range(level.width):
                for y in range(level.height):
                    room = level.room_at(x, y)
                    if room is not None and room.type == room_type:
                        data.append(LearnableRoom(room))
        return WFCRoomGenerator(room_type, data=data)

    @staticmethod
    def from_json_dicts(room_type: AreaType, json_pos: Dict[str, Dict[str, str]],
                        json_type: Dict[str, Dict[str, str]]) -> Optional["WFCRoomGenerator"]:
        pos_weights: Dict[Coordinate, Dict[LearnableRoom.TileData, int]] = {}
        for str_pos in json_pos:
            pos = Coordinate.from_string(str_pos)
            if pos is None: return None     # todo: maybe just skip instead? the remaining data might still be valuable

            pos_weights[pos] = {}
            for key, value in json_pos[str_pos].items():
                tile_data = LearnableRoom.TileData.from_string(key)
                weight = int(value)
                pos_weights[pos][tile_data] = weight

        type_weights: Dict[Optional[LearnableRoom.TileData], Dict[LearnableRoom.TileData, int]] = {}
        for str_type in json_type:
            tile_data = LearnableRoom.TileData.from_string(str_type)
            type_weights[tile_data] = {}
            for key, value in json_type[str_type].items():
                neighbor_data = LearnableRoom.TileData.from_string(key)
                weight = int(value)
                type_weights[tile_data][neighbor_data] = weight

        return WFCRoomGenerator(room_type, pos_weights, type_weights)

    def __init__(self, room_type: AreaType, pos_weights: Optional[Dict[Coordinate, Dict[Any, int]]] = None,
                 type_weights: Optional[Dict[Optional[Any], Dict[Any, int]]] = None,
                 data: Optional[List[WFCLearnMatrix]] = None):
        self.__room_type = room_type
        super(WFCRoomGenerator, self).__init__(pos_weights, type_weights, data)

    @property
    def room_type(self) -> AreaType:
        return self.__room_type

    def generate(self, seed: int, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Tile]] = None,
                 is_assignable: Optional[Callable[[LearnableRoom.TileData, Tile], bool]] = None) \
            -> List[List[LearnableRoom.TileData]]:
        if is_assignable is None:
            def is_assignable(key: LearnableRoom.TileData, value: Tile) -> bool:
                return key.code == value.code
        return super().generate(seed, width, height, static_entries, is_assignable)


class WFCEmptyRoomGenerator(WFCGenerator):
    def generate(self, seed: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                 static_entries: Optional[Dict[Coordinate, Any]] = None,
                 is_assignable: Optional[Callable[[LearnableRoom.TileData, Tile], bool]] = None) \
            -> List[List[LearnableRoom.TileData]]:
        if width is None: width = MapConfig.room_width()
        if height is None: height = MapConfig.room_height()
        # return an empty room (only Floor tiles)
        return [[LearnableRoom.TileData(TileCode.Floor, None) for _ in range(width)] for _ in range(height)]
