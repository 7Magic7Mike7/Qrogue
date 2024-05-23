from typing import List, Callable, Optional

from qrogue.game.logic.actors import Robot
from qrogue.game.world.navigation import Coordinate
from .map import Map, MapType, Room, MapMetaData


class LevelMap(Map):
    def __init__(self, meta_data: MapMetaData, file_name: str, seed: int, rooms: List[List[Optional[Room]]],
                 robot: Robot, spawn_room: Coordinate, check_achievement_callback: Callable[[str], bool],
                 trigger_event_callback: Callable[[str], None]):
        super().__init__(meta_data, file_name, seed, rooms, robot, spawn_room, check_achievement_callback,
                         trigger_event_callback)

    def get_type(self) -> MapType:
        return MapType.Level
