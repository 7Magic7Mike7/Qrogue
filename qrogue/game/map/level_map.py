from typing import List

from qrogue.game.achievements import AchievementManager
from qrogue.game.actors.robot import Robot
from qrogue.game.map.map import Map
from qrogue.game.map.navigation import Coordinate
from qrogue.game.map.rooms import Room


class LevelMap(Map):
    def __init__(self, name: str, seed: int, rooms: List[List[Room]], robot: Robot, spawn_room: Coordinate,
                 achievement_manager: AchievementManager):
        super().__init__(name, seed, rooms, robot, spawn_room, achievement_manager)

    def is_world(self) -> bool:
        return False
