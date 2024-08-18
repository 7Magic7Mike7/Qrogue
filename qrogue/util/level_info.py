from datetime import datetime
from typing import Dict, List, Optional, Callable

from .achievements import Unlocks
from .config import MapConfig, GameplayConfig, PathConfig, MapGrammarConfig, ScoreConfig, GateType
from .stv_difficulty import StvDifficulty
from .util_functions import datetime2str


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
            MapConfig.first_uncleared(): "l0k0v0",
            "l0k0v4": f"{MapConfig.expedition_map_prefix()}",
        },
        1: {
            MapConfig.first_uncleared(): "l0k1v0",
            "l0k1v4": f"{MapConfig.expedition_map_prefix()}",
        },
    }

    __LEVEL_COMPLETION_UNLOCKS: Dict[str, List[Unlocks]] = {
        # newbie tutorials
        "l0k0v0": [Unlocks.MainMenuContinue, Unlocks.ShowEnergy, ],
        "l0k0v1": [Unlocks.ShowEquation, Unlocks.PuzzleHistory],
        "l0k0v4": [Unlocks.LevelSelection, Unlocks.Workbench],

        # experienced tutorials are copied from newbie tutorials entered in init()

        # other levels
    }

    __LEVEL_COMPLETION_UNLOCKED_GATES: Dict[str, List[GateType]] = {
        # newbie tutorials
        "l0k0v0": [GateType.XGate],
        "l0k0v1": [GateType.CXGate],
        "l0k0v2": [],
        "l0k0v3": [GateType.HGate],
        "l0k0v4": [GateType.SGate],

        # experienced tutorials are copied from newbie tutorials entered in init()

        # other levels
    }

    __LEVEL_START_GATES: Dict[str, List[GateType]] = {      # todo: parse from level file instead?
        # newbie tutorials
        "l0k0v0": [GateType.XGate],
        "l0k0v1": [GateType.XGate],
        "l0k0v2": [GateType.XGate],
        "l0k0v3": [GateType.XGate, GateType.CXGate],
        "l0k0v4": [GateType.XGate, GateType.CXGate, GateType.HGate],

        # experienced tutorials are copied from newbie tutorials entered in init()

        # other levels
    }

    # for converting internal names to display names and vice versa
    __NAME_CONVERTER: Dict[str, str] = {}  # is filled dynamically within LevelInfo.init()

    @staticmethod
    def init():
        # initialize map order in-between tutorials
        start, end = 0, 3
        for i in range(start, end + 1):
            for km in [0, 1]:
                src_name, dst_name = f"l0k{km}v{i}", f"l0k{km}v{i + 1}"
                LevelInfo.__MAP_ORDER[km][src_name] = dst_name

        def init_experienced_tutorials(target_dict: Dict[str, List]):
            values_to_add: Dict[str, List] = {}
            for name in target_dict:
                if name[2:4] != "k0": continue
                exp_name = name[:2] + "k1" + name[4:]
                values_to_add[exp_name] = target_dict[name].copy()
            for name in values_to_add:
                target_dict[name] = values_to_add[name]

        # initialize completion unlocks for experienced tutorials
        init_experienced_tutorials(LevelInfo.__LEVEL_COMPLETION_UNLOCKS)

        # initialize gate unlocks for experienced tutorials
        init_experienced_tutorials(LevelInfo.__LEVEL_COMPLETION_UNLOCKED_GATES)

        # initialize level start gates for experienced tutorials
        init_experienced_tutorials(LevelInfo.__LEVEL_START_GATES)

        # initialize __NAME_CONVERTER
        for mode in LevelInfo.__MAP_ORDER.keys():
            for level in LevelInfo.__MAP_ORDER[mode]:
                if level == MapConfig.first_uncleared(): continue

                data = PathConfig.read_level(level, in_dungeon_folder=True)
                start = data.index(MapGrammarConfig.name_prefix()) + len(MapGrammarConfig.name_prefix())
                end = data.index(MapGrammarConfig.description_prefix()) - 1  # subtract the new line before description
                display_name = data[start + 1:end - 1]  # also remove the enclosing quotes

                LevelInfo.__NAME_CONVERTER[level] = display_name

    @staticmethod
    def extract_knowledge_mode(cur_map: str) -> Optional[int]:
        if "k" in cur_map and "v" in cur_map:
            km = cur_map[cur_map.index("k") + 1:cur_map.index("v")]
            if km.isdigit():
                return int(km)
            else:
                from qrogue.util import Config
                Config.check_reachability("LevelInfo.extract_knowledge_mode(): invalid knowledge mode")
        return None

    @staticmethod
    def get_next(cur_map: str, is_level_completed: Callable[[str], bool]) -> Optional[str]:
        """
        :param cur_map: internal name of the map we want to get the next map's internal name for
        :param is_level_completed: Callable to find out which levels are already completed in case cur_map equals the
                                    meta name MapConfig.first_uncleared()
        :return: the internal name of cur_map's next map or None if there is no next map
        """
        knowledge_mode = LevelInfo.extract_knowledge_mode(cur_map)
        if knowledge_mode is None:
            knowledge_mode = GameplayConfig.get_knowledge_mode()

        if cur_map == MapConfig.first_uncleared():
            next_map = LevelInfo.__MAP_ORDER[knowledge_mode][cur_map]
            while is_level_completed(next_map):
                if next_map in LevelInfo.__MAP_ORDER[knowledge_mode]:
                    next_map = LevelInfo.__MAP_ORDER[knowledge_mode][next_map]
                else:
                    break
            return next_map
        elif cur_map in LevelInfo.__MAP_ORDER[knowledge_mode]:
            return LevelInfo.__MAP_ORDER[knowledge_mode][cur_map]
        elif cur_map.startswith(MapConfig.expedition_map_prefix()):
            return MapConfig.expedition_map_prefix()
        return None

    @staticmethod
    def get_prev(cur_map: str, is_level_completed: Callable[[str], bool]) -> Optional[str]:
        """
        :param cur_map: internal name of the map we want to get the previous map's internal name for
        :param is_level_completed: Callable to find out which levels are already completed in case cur_map equals the
                                    meta name MapConfig.first_uncleared()
        :return: the internal name of cur_map's previous map or None if there is no previous map
        """
        if cur_map == MapConfig.first_uncleared():
            cur_map = LevelInfo.get_prev(LevelInfo.get_next(cur_map, is_level_completed), is_level_completed)
        knowledge_mode = LevelInfo.extract_knowledge_mode(cur_map)
        if knowledge_mode is None:
            knowledge_mode = GameplayConfig.get_knowledge_mode()

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
            return unlocks
        else:
            if level_name in LevelInfo.__LEVEL_COMPLETION_UNLOCKS:
                return LevelInfo.__LEVEL_COMPLETION_UNLOCKS[level_name]
            return []

    @staticmethod
    def get_level_completion_unlocked_gates(level_name: str, is_level_completed: Callable[[str], bool],
                                            include_previous_levels: bool = False) -> List[GateType]:
        if include_previous_levels:
            gates = []
            while level_name is not None:
                gates += LevelInfo.get_level_completion_unlocked_gates(level_name, is_level_completed,
                                                                       include_previous_levels=False)
                level_name = LevelInfo.get_prev(level_name, is_level_completed)
            return gates
        else:
            if level_name in LevelInfo.__LEVEL_COMPLETION_UNLOCKED_GATES:
                return LevelInfo.__LEVEL_COMPLETION_UNLOCKED_GATES[level_name]
            return []

    @staticmethod
    def get_level_start_gates(level_name: str) -> List[GateType]:
        """
        Provides a list of GateType based on which gates the player has when starting a level without special settings
        (i.e., on the first play-through).

        :param level_name: internal name of the level we want to get the starting gates for
        :return: list of GateType corresponding to the gates the player has as the beginning of the referenced level
        """
        if level_name in LevelInfo.__LEVEL_START_GATES:
            return LevelInfo.__LEVEL_START_GATES[level_name]
        return []

    @staticmethod
    def convert_to_display_name(internal_name: str, allow_display_name: bool = True) -> Optional[str]:
        """
        Returns: the display name corresponding to the provided level name or None if no level name was provided
        Args:
            internal_name: the internal name of the level we want to retrieve the display name of
            allow_display_name: whether we allow internal_name to already be a display name and return it in case it is
        """
        if internal_name.startswith(MapConfig.expedition_map_prefix()):
            from qrogue.util import Config
            Config.check_reachability(f"LevelInfo.convert_to_display_name({internal_name})")
            return f"Expedition"

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

    @staticmethod
    def get_expedition_difficulty(expedition_progress: int) -> int:
        # level is at least 1 and at most max_difficulty_level
        return min(max(int(expedition_progress / 10), StvDifficulty.min_difficulty_level()),
                   StvDifficulty.max_difficulty_level())


class LevelData:
    def __init__(self, name: str, date_time: datetime, duration: int, score: int):
        if name.endswith("done"):
            self.__name = name[:-len("done")]
        else:
            self.__name = name
        self.__date_time = date_time
        self.__duration = duration
        self.__score = score
        self.__time_bonus = ScoreConfig.compute_time_bonus(score, duration)

    @property
    def name(self) -> str:
        """

        Returns: internal name of the map

        """
        return self.__name

    @property
    def is_level(self) -> bool:
        return self.__name.startswith(MapConfig.level_map_prefix())

    @property
    def date_time(self) -> datetime:
        return self.__date_time

    @property
    def duration(self) -> int:
        return self.__duration

    @property
    def score(self) -> int:
        return self.__score

    @property
    def time_bonus(self) -> int:
        return self.__time_bonus

    @property
    def total_score(self) -> int:
        return self.__score + self.__time_bonus

    @property
    def knowledge_mode(self) -> Optional[int]:
        return LevelInfo.extract_knowledge_mode(self.__name)

    @property
    def level_num(self) -> Optional[int]:
        if "v" in self.__name:
            level_num = self.__name[self.__name.index("v")+1:]
            if level_num.isdigit():
                return int(level_num)
        return None

    def __str__(self) -> str:
        return f"{self.__name} ({datetime2str(self.__date_time)}, {self.__duration}s, " \
               f"#{self.total_score})"
