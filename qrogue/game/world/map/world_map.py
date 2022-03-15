from typing import List, Callable

from qrogue.game.logic.actors import Player
from qrogue.game.world.navigation import Coordinate

from qrogue.game.world.map import Map, MapType, Room


class WorldMap(Map):
    def __init__(self, name: str, file_name: str, seed: int, rooms: List[List[Room]], player: Player,
                 spawn_room: Coordinate, check_achievement_callback: Callable[[str], bool],
                 trigger_achievement_callback: Callable[[str], None]):
        super().__init__(name, file_name, seed, rooms, player, spawn_room, check_achievement_callback,
                         trigger_achievement_callback)

    def get_type(self) -> MapType:
        return MapType.World
