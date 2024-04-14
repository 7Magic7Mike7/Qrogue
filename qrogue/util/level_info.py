from typing import Dict, List, Optional, Callable

from qrogue.util import MapConfig, GameplayConfig, PathConfig, MapGrammarConfig
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

    # for converting internal names to display names and vice versa
    __NAME_CONVERTER: Dict[str, str] = {}   # is filled dynamically within LevelInfo.init()

    @staticmethod
    def init():
        # initialize __NAME_CONVERTER
        for mode in LevelInfo.__MAP_ORDER.keys():
            for level in LevelInfo.__MAP_ORDER[mode]:
                if level == MapConfig.first_uncleared(): continue

                data = PathConfig.read_level(level, in_dungeon_folder=True)
                start = data.index(MapGrammarConfig.name_prefix()) + len(MapGrammarConfig.name_prefix())
                end = data.index(MapGrammarConfig.description_prefix()) - 1  # subtract the new line before description
                display_name = data[start+1:end-1]      # also remove the enclosing quotes

                LevelInfo.__NAME_CONVERTER[level] = display_name

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

    @staticmethod
    def convert_to_display_name(internal_name: str, allow_display_name: bool = True) -> Optional[str]:
        """
        Returns: the display name corresponding to the provided level name or None if no level name was provided
        Args:
            internal_name: the internal name of the level we want to retrieve the display name of
            allow_display_name: whether we allow internal_name to already be a display name and return it in case it is
        """
        if internal_name in LevelInfo.__NAME_CONVERTER:
            return LevelInfo.__NAME_CONVERTER[internal_name]

        if allow_display_name:
            # this call cannot allow an internal name to avoid an endless recursion
            return LevelInfo.convert_to_internal_name(internal_name, allow_internal_name=False)
        return None

    @staticmethod
    def convert_to_internal_name(display_name: str, allow_internal_name: bool = True) -> Optional[str]:
        """
        Returns: the internal name corresponding to the provided level name or None if no level name was provided
        Args:
            display_name: the display name of the level we want to retrieve the internal name of
            allow_internal_name: whether we allow display_name to already be an internal name and return it in that case
        """
        for internal in LevelInfo.__NAME_CONVERTER:
            if LevelInfo.__NAME_CONVERTER[internal] == display_name:
                return internal

        if allow_internal_name:
            # this call cannot allow a display name to avoid an endless recursion
            return LevelInfo.convert_to_display_name(display_name, allow_display_name=False)
        return None
