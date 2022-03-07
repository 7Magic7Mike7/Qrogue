from typing import List, Callable

from qrogue.game.actors.player import Player
from qrogue.game.map.map import Map
from qrogue.game.map.navigation import Coordinate
from qrogue.game.map.rooms import Room


class WorldMap(Map):
    def __init__(self, name: str, seed: int, rooms: List[List[Room]], player: Player, spawn_room: Coordinate,
                 proceed_to_next_map: Callable[[], None]):
        super().__init__(name, seed, rooms, player, spawn_room, proceed_to_next_map)

    def is_world(self) -> bool:
        return True
