from typing import List, Callable

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.map import Map, MapType, Room, MapMetaData
from qrogue.game.world.navigation import Coordinate


class ExpeditionMap(Map):
    def __init__(self, seed: int, rooms: List[List[Room]], controllable: Controllable, spawn_room: Coordinate,
                 check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None]):
        def show_description():
            pass    # expeditions don't have anything to show at the moment
        meta_data = MapMetaData(f"Expedition {seed}", None, True, show_description)
        super().__init__(meta_data, f"exp{seed}", seed, rooms, controllable, spawn_room, check_achievement,
                         trigger_event)

    def get_type(self) -> MapType:
        return MapType.Expedition
