from typing import Dict, List, Optional, Callable

from qrogue.util import MapConfig, GameplayConfig
from qrogue.util.achievements import Unlocks


class LevelInfo:
    __MAP_ORDER: Dict[int, Dict[str, str]] = {
        # map names:
        #   - the first character determines if it's a level ("l") or world ("w")
        #   - the second character determines to which world the map belongs to
        #   - the third character determines if the level differs based on knowledge mode, followed by the corresponding
        #     digit of the knowledge mode
        #   - last digit for levels is used to order the levels (only for structure, not used in game logic)
        #   - alternatively maps can also start with "expedition" to mark them as generated
        0: {
            # MapConfig.spaceship(): MapConfig.intro_level(),
            MapConfig.first_uncleared(): "l0k0v0",
            "l0k0v0": "l0k0v1",
            "l0k0v1": "l0k0v2",
            "l0k0v2": "l0k0v3",
            "l0k0v3": "l0k0v4",
            "l0k0v4": f"{MapConfig.expedition_map_prefix()}25",
            "l0training": "w0",
            "l0exam": MapConfig.spaceship(),
            "w0": MapConfig.spaceship(),

            MapConfig.hub_world(): "l0v0",
        },
        1: {
            MapConfig.first_uncleared(): "l0k1v0",
            "l0k1v0": "l0k1v1",
            "l0k1v1": "l0k1v2",
            "l0k1v2": "l0k1v3",
            "l0k1v3": "l0k1v4",
            "l0k1v4": f"{MapConfig.expedition_map_prefix()}25",
        },
    }

    __LEVEL_COMPLETION_UNLOCKS: Dict[str, List[Unlocks]] = {
        # newbie tutorials
        "l0k0v0": [Unlocks.MainMenuContinue, Unlocks.ShowEnergy, ],
        "l0k0v1": [Unlocks.ShowEquation],

        # experienced tutorials
        "l0k1v0": [Unlocks.MainMenuContinue, Unlocks.ShowEnergy, ],
        "l0k1v1": [Unlocks.ShowEquation],

        # other levels
    }

    @staticmethod
    def get_next(cur_map: str, is_level_completed: Callable[[str], bool]) -> Optional[str]:
        if cur_map == MapConfig.first_uncleared():
            next_map = LevelInfo.__MAP_ORDER[GameplayConfig.get_knowledge_mode()][cur_map]
            while is_level_completed(next_map):
                if next_map in LevelInfo.__MAP_ORDER[GameplayConfig.get_knowledge_mode()]:
                    next_map = LevelInfo.__MAP_ORDER[GameplayConfig.get_knowledge_mode()][next_map]
                else:
                    break
            return next_map
        elif cur_map in LevelInfo.__MAP_ORDER[GameplayConfig.get_knowledge_mode()]:
            return LevelInfo.__MAP_ORDER[GameplayConfig.get_knowledge_mode()][cur_map]
        return None

    @staticmethod
    def get_prev(cur_map: str, is_level_completed: Callable[[str], bool]) -> Optional[str]:
        if cur_map == MapConfig.first_uncleared():
            cur_map = LevelInfo.get_prev(LevelInfo.get_next(cur_map, is_level_completed), is_level_completed)
        # todo: implement more dynamically?
        knowledge_mode = GameplayConfig.get_knowledge_mode()
        if "l" in cur_map and "k" in cur_map:
            km = cur_map[cur_map.index("l") + 1:cur_map.index("k")]
            if km.isdigit():
                knowledge_mode = km
            else:
                debug_me = True

        if cur_map.startswith(MapConfig.expedition_map_prefix()):
            return f"l0k{knowledge_mode}v4"  # last level
        else:
            level = cur_map[cur_map.index("v") + 1:]
            if level.isnumeric() and level != "0":
                level = int(level) - 1
            else:
                return None
            return f"l0k{knowledge_mode}v{level}"

    @staticmethod
    def get_level_completion_unlocks(level_name: str, is_level_completed: Callable[[str], bool],
                                     include_previous_levels: bool = False) -> List[Unlocks]:
        if include_previous_levels:
            unlocks = []
            while level_name is not None:
                unlocks += LevelInfo.get_level_completion_unlocks(level_name, is_level_completed,
                                                                  include_previous_levels=False)
                level_name = LevelInfo.get_prev(level_name, is_level_completed)
        else:
            if level_name in LevelInfo.__LEVEL_COMPLETION_UNLOCKS:
                return LevelInfo.__LEVEL_COMPLETION_UNLOCKS[level_name]
            return []
