from typing import List, Callable

from qrogue.game.logic.actors import Robot
from qrogue.game.world.navigation import Coordinate

from qrogue.game.world.map import Map
from qrogue.game.world.map import Room


class LevelMap(Map):
    def __init__(self, name: str, seed: int, rooms: List[List[Room]], robot: Robot, spawn_room: Coordinate,
                 check_achievement_callback: Callable[[str], bool], trigger_event_callback: Callable[[str], None]):
        super().__init__(name, seed, rooms, robot, spawn_room, check_achievement_callback, trigger_event_callback)

    def is_world(self) -> bool:
        return False
