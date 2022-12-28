from typing import List, Callable, Optional

from qrogue.game.logic.actors import Controllable
from qrogue.game.world.map import Map, MapType, Room, MapMetaData
from qrogue.game.world.navigation import Coordinate
from qrogue.util import MapConfig


class ExpeditionMap(Map):
    def __init__(self, seed: int, rooms: List[List[Optional[Room]]], controllable: Controllable, spawn_room: Coordinate,
                 check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None]):
        def show_description():
            pass    # expeditions don't have anything to show at the moment
        meta_data = MapMetaData(f"Expedition {seed}", None, True, show_description)
        super().__init__(meta_data, f"{MapConfig.expedition_map_prefix()}{seed}", seed, rooms, controllable, spawn_room,
                         check_achievement, trigger_event)

    def get_type(self) -> MapType:
        return MapType.Expedition
