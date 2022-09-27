from typing import List, Callable, Set, Iterator

from qrogue.game.logic.actors import Player
from qrogue.game.world.navigation import Coordinate

from qrogue.game.world.map import Map, MapType, Room, MapMetaData


class WorldMap(Map):
    def __init__(self, meta_data: MapMetaData, file_name: str, seed: int, rooms: List[List[Room]], player: Player,
                 spawn_room: Coordinate, check_achievement_callback: Callable[[str], bool],
                 trigger_achievement_callback: Callable[[str], None], mandatory_levels: Set[str]):
        super().__init__(meta_data, file_name, seed, rooms, player, spawn_room, check_achievement_callback,
                         trigger_achievement_callback)
        self.__mandatory_levels: Set[str] = mandatory_levels

    @property
    def num_of_mandatory_levels(self) -> int:
        return len(self.__mandatory_levels)

    def get_type(self) -> MapType:
        return MapType.World

    def is_mandatory_level(self, internal_level_name: str) -> bool:
        return internal_level_name in self.__mandatory_levels

    def mandatory_level_iterator(self) -> Iterator[str]:
        return iter(self.__mandatory_levels)
