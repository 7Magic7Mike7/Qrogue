from typing import List, Callable, Optional

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.navigation import Coordinate
from qrogue.util import MapConfig, StvDifficulty
from .map import Map, MapType, Room, MapMetaData


class ExpeditionMap(Map):
    __NAME_CHARS = "".join([f"{chr(c)}{chr(c).lower()}" for c in range(65, 65 + 26)])

    @staticmethod
    def to_display_name(difficulty: StvDifficulty, seed: int) -> str:
        display_name = "Expedition "
        index = 0
        for diff_level in difficulty.to_code():
            level = int(diff_level)
            if index + level >= len(ExpeditionMap.__NAME_CHARS):
                # restart if we overshoot (depends on the number of existing DifficultyTypes)
                index -= len(ExpeditionMap.__NAME_CHARS)
                # indicate the overshoot so expeditions with different difficulties don't accidentally get the same name
                display_name += "-"
            display_name += ExpeditionMap.__NAME_CHARS[index + level]
            index += StvDifficulty.max_difficulty_level()
        return display_name + f"{difficulty.level}*{seed}"

    def __init__(self, seed: int, difficulty: StvDifficulty, rooms: List[List[Optional[Room]]],
                 controllable: Controllable, spawn_room: Coordinate, check_achievement: Callable[[str], bool],
                 trigger_event: Callable[[str], None]):
        # expeditions don't have a description to show, so we pass an empty lambda
        meta_data = MapMetaData(ExpeditionMap.to_display_name(difficulty, seed), None, True, lambda: None)
        super().__init__(meta_data, f"{MapConfig.expedition_map_prefix()}{seed}", seed, rooms, controllable, spawn_room,
                         check_achievement, trigger_event)

    def get_type(self) -> MapType:
        return MapType.Expedition
