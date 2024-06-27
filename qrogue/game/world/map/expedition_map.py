from typing import List, Callable, Optional

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.navigation import Coordinate
from qrogue.util import MapConfig, StvDifficulty, RandomManager
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
            offset = rm.get_int(min_=1, max_=len(ExpeditionMap.__NAME_CHARS) - StvDifficulty.max_difficulty_level())
            character = ExpeditionMap.__get_character(index + int(diff_level), offset)
            index += StvDifficulty.max_difficulty_level() + offset
            # the first letter is always upper case
            if i == 0: display_name += character.upper()
            else: display_name += character
        return display_name + f"{difficulty.level}*{seed}"

    def __init__(self, seed: int, difficulty: StvDifficulty, rooms: List[List[Optional[Room]]],
                 controllable: Controllable, spawn_room: Coordinate, check_achievement: Callable[[str], bool],
                 trigger_event: Callable[[str], None]):
        # expeditions don't have a description to show, so we pass an empty lambda
        meta_data = MapMetaData(ExpeditionMap.to_display_name(difficulty, seed), None, True, lambda: None)
        self.__diff_level = difficulty.level
        super().__init__(meta_data, f"{MapConfig.expedition_map_prefix()}{seed}", seed, rooms, controllable, spawn_room,
                         check_achievement, trigger_event)

    @property
    def difficulty_level(self) -> int:
        return self.__diff_level

    def get_type(self) -> MapType:
        return MapType.Expedition
