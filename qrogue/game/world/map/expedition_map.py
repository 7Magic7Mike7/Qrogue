from typing import List, Callable, Optional, Any, Tuple

from qrogue.game.logic.actors import Controllable
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.navigation import Coordinate
from qrogue.util import MapConfig, StvDifficulty, RandomManager, GateType, DifficultyType
from .map import Map, MapType, Room, MapMetaData


class ExpeditionMap(Map):
    # chosen characters:
    #  - Q: because quantum (disregarded for the other criteria)
    #  - (almost) the same number of consonants (13) and vowels (13)
    #  - (almost) the same number of lower (12) and upper (14) case letters
    #  - characters that look cool/spacy appear more often while maintaining the other criteria
    __NAME_CHARS = "XXxZzBFHTYcvwAaEeIIiUuuOooQQQ"

    @staticmethod
    def __get_character(value: int, offset: Optional[int] = None) -> str:
        if offset is not None: value += offset
        value %= len(ExpeditionMap.__NAME_CHARS)
        return ExpeditionMap.__NAME_CHARS[value]

    @staticmethod
    def to_display_name(difficulty: StvDifficulty, seed: int) -> str:
        rm = RandomManager.create_new(seed)
        display_name = "Expedition "
        index = 0
        for i, diff_level in enumerate(difficulty.to_code()):
            # offset makes it so the next character is definitely different
            offset = rm.get_int(min_=1, max_=len(ExpeditionMap.__NAME_CHARS) - StvDifficulty.num_of_difficulty_levels())
            character = ExpeditionMap.__get_character(index + int(diff_level), offset)
            index += StvDifficulty.num_of_difficulty_levels() + offset
            # the first letter is always upper case
            if i == 0: display_name += character.upper()
            else: display_name += character
        return display_name + f"{difficulty.level}*{seed}"

    @staticmethod
    def validate_gates_for_difficulty(difficulty: StvDifficulty, gates: List[Instruction]) -> Tuple[int, Any]:
        """
        Return codes:
            - 0 = valid
            - 1 = not enough gates, returns (needed number of gates, actual number of gates)
            - 2 = not enough unique gates, returns (needed number of unique gates, actual unique gates)
            - 3 = gates are not difficult enough, returns (needed difficulty sum, actual difficulty sum)

        :param difficulty: the StvDifficulty to validate for
        :param gates: a list of Instructions we want to validate
        :return: (0, None) if gates are valid for the given difficulty, other values depending on what is invalid

        """
        needed_num_of_gates = difficulty.get_absolute_value(DifficultyType.MinAvailableGates, 0, 0)
        num_of_gates = len(gates)
        if num_of_gates < needed_num_of_gates:
            return 1, (needed_num_of_gates, num_of_gates)

        needed_unique_gates = difficulty.get_absolute_value(DifficultyType.MinGateVariety, 0, 0)
        unique_gates = set(gates)
        if len(unique_gates) < needed_unique_gates:
            return 2, (needed_unique_gates, unique_gates)

        needed_diff_sum = difficulty.get_absolute_value(DifficultyType.MinGateDifficulty, 0, 0)
        difficulty_sum = sum([gate.difficulty for gate in gates])
        if difficulty_sum < needed_diff_sum:
            return 3, (needed_diff_sum, difficulty_sum)

        return 0, None

    def __init__(self, seed: int, difficulty: StvDifficulty, main_gate: GateType, rooms: List[List[Optional[Room]]],
                 controllable: Controllable, spawn_room: Coordinate, check_achievement: Callable[[str], bool],
                 trigger_event: Callable[[str], None]):
        # expeditions don't have a description to show, so we pass an empty lambda
        meta_data = MapMetaData(ExpeditionMap.to_display_name(difficulty, seed), None, True, lambda: None)
        self.__difficulty = difficulty
        self.__main_gate = main_gate
        super().__init__(meta_data, f"{MapConfig.expedition_map_prefix()}{difficulty.to_code()}", seed, rooms,
                         controllable, spawn_room, check_achievement, trigger_event)

    @property
    def difficulty(self) -> StvDifficulty:
        return self.__difficulty

    @property
    def main_gate(self) -> GateType:
        return self.__main_gate

    def get_type(self) -> MapType:
        return MapType.Expedition
