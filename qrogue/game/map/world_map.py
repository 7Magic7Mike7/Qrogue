from typing import List

from qrogue.game.achievements import AchievementManager
from qrogue.game.actors.player import Player
from qrogue.game.map.map import Map
from qrogue.game.map.navigation import Coordinate
from qrogue.game.map.rooms import Room


class WorldMap(Map):
    def __init__(self, name: str, seed: int, rooms: List[List[Room]], player: Player, spawn_room: Coordinate,
                 achievement_manager: AchievementManager):
        super().__init__(name, seed, rooms, player, spawn_room, achievement_manager)

    def is_world(self) -> bool:
        return True
