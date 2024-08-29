import time
from threading import Thread
from typing import Callable, Optional, Dict, List, Tuple, Union

from qrogue.game.logic import Message
from qrogue.game.logic.actors.controllables.robot import RoboProperties
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.world.dungeon_generator import ExpeditionGenerator, QrogueLevelGenerator
from qrogue.game.world.dungeon_generator.wave_function_collapse import WFCManager
from qrogue.game.world.map import Map, MapType, ExpeditionMap, CallbackPack
from qrogue.game.world.navigation import Coordinate
from qrogue.graphics.popups import Popup
from qrogue.management.save_data import NewSaveData
from qrogue.util import CommonQuestions, RandomManager, LevelInfo, Config, MapConfig, ErrorConfig, \
    ExpeditionConfig, StvDifficulty
from qrogue.util.achievements import Achievement
from qrogue.util.util_functions import cur_datetime, time_diff


class MapManager:
    @staticmethod
    def parse_expedition_parameters(map_name: str, map_seed: Optional[int], expedition_progress: int) \
            -> Tuple[str, int, Optional[int]]:
        # Example: expedition0d7p11 -> Difficulty = 0, map seed = 7, puzzle seed = 11
        # first: extract difficulty and seed information from map_name if available
        if len(map_name) > len(MapConfig.expedition_map_prefix()):
            # map_name contains additional information
            info = map_name[len(MapConfig.expedition_map_prefix()):]

            def parse_seed_info(_seed_info: str) -> Tuple[Optional[int], int]:
                # seed info is either solely for map_seed or for both type of seeds
                if MapConfig.puzzle_seed_separator() in _seed_info:
                    # info_seed contains information about both seeds
                    _info_puzzle, _info_map = _seed_info.split(MapConfig.puzzle_seed_separator())
                    return int(_info_puzzle), int(_info_map)
                else:
                    # _seed_info only contains information about map_seed
                    return None, int(_seed_info)

            if MapConfig.diff_code_separator() in info:
                diff_code, info_seed = info.split(MapConfig.diff_code_separator())
                # info contains both difficulty and seed information
                if map_seed is None or MapConfig.puzzle_seed_separator() in info_seed:
                    puzzle_seed, map_seed = parse_seed_info(info_seed)
                else:
                    # seed info is solely for puzzle_seed
                    puzzle_seed = int(info_seed)
            elif map_seed is None:
                # there is no difficulty code, just seed information (map_seed is implicitly None due to 1st if)
                expedition_progress = int(expedition_progress)
                diff_code = str(LevelInfo.get_expedition_difficulty(expedition_progress))
                puzzle_seed, map_seed = parse_seed_info(info)
                Config.check_reachability("load_map(): expedition without seed")
            else:
                # a map_seed was provided and there is no diff_code separator -> info is solely for diff_code
                diff_code = info
                puzzle_seed = None
        else:
            # no additional information given, hence, we use default values
            diff_code = str(LevelInfo.get_expedition_difficulty(expedition_progress))
            puzzle_seed = None

        assert map_seed is not None, "MapSeed is None after parsing expedition arguments!"
        return diff_code, map_seed, puzzle_seed

    def __init__(self, wfc_manager: WFCManager, save_data: NewSaveData, seed: int, start_level: Callable[[Map], None],
                 start_level_transition_callback: Callable[[str, str, Callable[[], None]], None],
                 exit_map_callback: Callable[[], None], callback_pack: CallbackPack,
                 queue_size: int = ExpeditionConfig.DEFAULT_QUEUE_SIZE):
        self.__save_data = save_data
        # no longer used code!
        self.__exit_map = exit_map_callback
        self.__cbp = callback_pack
        self.__queue_size = queue_size

        self.__rm = RandomManager.create_new(seed)
        self.__start_level = start_level
        self.__start_level_transition = start_level_transition_callback
        self.__expedition_generator = ExpeditionGenerator(wfc_manager, self.__save_data.check_achievement,
                                                          self.trigger_event, self.__load_back,
                                                          save_data.get_gates, callback_pack)  # todo: pass ExpeditionGenerator as argument?
        self.__expedition_queue: List[ExpeditionMap] = []
        self.__cur_map: Optional[Map] = None

        self.__level_timer = cur_datetime()
        self.__temp_level_event_storage: Dict[str, Tuple[int, int]] = {}  # event name -> score, done_score

    @property
    def is_in_level(self) -> bool:
        return self.__cur_map is not None and self.__cur_map.get_type() is MapType.Level

    @property
    def is_in_expedition(self) -> bool:
        return self.__cur_map is not None and self.__cur_map.get_type() is MapType.Expedition

    @property
    def show_individual_qubits(self) -> bool:
        return self.__cur_map.show_individual_qubits

    def fill_expedition_queue(self, callback: Optional[Callable[[], None]] = None, no_thread: bool = False):
        if len(self.__expedition_queue) >= self.__queue_size:
            return

        def fill():
            robo_props = RoboProperties()   # todo: which property values to use?
            while len(self.__expedition_queue) < self.__queue_size:
                # todo: how to handle difficulty?
                difficulty = StvDifficulty.from_difficulty_code("1", robo_props.num_of_qubits, robo_props.circuit_space)
                map_seed = self.__rm.get_seed("MapManager.fill()@map_seed")
                puzzle_seed = self.__rm.get_seed("MapManager.fill()@puzzle_seed")
                expedition, success = self.__expedition_generator.generate(map_seed, (robo_props, difficulty, puzzle_seed))
                if success:
                    self.__expedition_queue.append(expedition)

            if callback is not None:
                callback()

        if no_thread:
            fill()
        else:
            Thread(target=fill, args=(), daemon=True).start()

    def __load_level(self, map_name: str, spawn_room: Optional[Coordinate] = None, seed: Optional[int] = None,
                     gate_list: Optional[List[Instruction]] = None):
        # generate a random seed for all paths since the randomizer state should not depend on whether we passed a seed
        # manually (e.g., during debugging) or not
        rand_seed = self.__rm.get_seed("MapManager.__load_level()@seedForLevel")
        if seed is None: seed = rand_seed

        # todo maybe levels should be able to have arbitrary names except "w..." or "e..." or "back" or "next"?
        check_achievement = self.__save_data.check_achievement
        generator = QrogueLevelGenerator(check_achievement, self.trigger_event, self.load_map, Popup.npc_says,
                                         self.__cbp)
        try:
            level, success = generator.generate(seed, map_name)
            if success:
                self.__cur_map = level
                # if we have a valid gate_list, we try to set it and only show the error if it fails
                if gate_list is not None and not self.__cur_map.robot.set_available_instructions(gate_list):
                    Popup.error(f"Failed to set gates! Please make sure you don't have more than "
                                f"{self.__cur_map.robot.capacity} gates selected.")
                # else: available gates were determined by the level beforehand and don't change
                self.__start_level(self.__cur_map)
            else:
                Popup.error(f"Failed to generate level \"{map_name}\"!", add_report_note=True)
        except FileNotFoundError:
            Popup.error(ErrorConfig.invalid_map(map_name, f"Level-file for \"{map_name}\" was not found! "),
                        add_report_note=True)

    def __load_expedition(self, difficulty: Union[StvDifficulty, str], map_seed: Optional[int] = None,
                          puzzle_seed: Optional[int] = None, gate_list: Optional[List[Instruction]] = None) -> None:
        # generate random seeds for all paths since the randomizer state should not depend on whether we passed a seed
        # manually (e.g., during debugging) or not
        rand_map_seed = self.__rm.get_seed("MapManager.__load_expedition()@map_seed")
        rand_puzzle_seed = self.__rm.get_seed("MapManager.__load_expedition()@puzzle_seed")

        robo_props = RoboProperties(num_of_qubits=3, circuit_space=5, gate_list=gate_list)  # todo: currently these are just default values
        if isinstance(difficulty, str):
            difficulty = StvDifficulty.from_difficulty_code(difficulty, robo_props.num_of_qubits,
                                                            robo_props.circuit_space)
        if map_seed is None and self.__queue_size > 0:
            while len(self.__expedition_queue) <= 0:
                time.sleep(Config.loading_refresh_time())
            success = True
            expedition = self.__expedition_queue.pop(0)
            self.fill_expedition_queue()  # todo: how to handle difficulty? dictionary?
            Config.check_reachability("post queue filling")
        else:
            if map_seed is None: map_seed = rand_map_seed
            if puzzle_seed is None: puzzle_seed = rand_puzzle_seed
            expedition, success = self.__expedition_generator.generate(map_seed, (robo_props, difficulty,
                                                                                  puzzle_seed))

        if success:
            self.__cur_map = expedition
            self.__start_level(self.__cur_map)
        else:
            Popup.error(f"Failed to create an expedition for seed = {map_seed}. Please try again with a different "
                        f"seed or restart the game. Should the error keep occurring:", add_report_note=True)

    def load_map(self, map_name: str, spawn_room: Optional[Coordinate] = None, seed: Optional[int] = None,
                 gate_list: Optional[List[Instruction]] = None):
        if map_name == MapConfig.first_uncleared():
            next_map = LevelInfo.get_next(MapConfig.first_uncleared(), self.__save_data.check_level)
            if next_map is None:
                Popup.error(f"Failed to find the next map of \"{map_name}\". Please restart and try again.\n"
                            f"If this error still occurs but you're sure that the corresponding file is present:",
                            add_report_note=True)
            else:
                self.load_map(next_map, spawn_room, seed, gate_list)

        elif map_name.lower() == MapConfig.next_map_string():
            self.__load_next()

        elif map_name.lower() == MapConfig.back_map_string():
            self.__load_back()

        elif map_name.lower().startswith(MapConfig.level_map_prefix()):
            self.__load_level(map_name, spawn_room, seed, gate_list)

        elif map_name.lower().startswith(MapConfig.expedition_map_prefix()):
            expedition_progress = int(self.__save_data.get_progress(Achievement.CompletedExpedition)[0])
            diff_code, map_seed, puzzle_seed = MapManager.parse_expedition_parameters(map_name, seed,
                                                                                      expedition_progress)
            # load expedition
            self.__load_expedition(diff_code, map_seed, puzzle_seed, gate_list)

        else:
            Popup.error(ErrorConfig.invalid_map(map_name), add_report_note=True)

    def __load_next(self):
        # generate random seeds for all paths since the randomizer state should not depend on whether we passed a seed
        # manually (e.g., during debugging) or not
        rand_map_seed = self.__rm.get_seed("MapManager.load_next()@expedition>map_seed")
        rand_puzzle_seed = self.__rm.get_seed("MapManager.load_next()@expedition>puzzle_seed")

        next_map = LevelInfo.get_next(self.__cur_map.internal_name, self.__save_data.check_level)
        if next_map is None:
            error_text = ErrorConfig.invalid_map(self.__cur_map.name, f"Failed to load next map after "
                                                                      f"\"{self.__cur_map.name}\". ")
            Popup.error(error_text, add_report_note=True)

        elif next_map.startswith(MapConfig.expedition_map_prefix()):
            # create difficulty code based on expedition progress
            expedition_progress = int(self.__save_data.get_progress(Achievement.CompletedExpedition)[0])
            diff_code = str(LevelInfo.get_expedition_difficulty(expedition_progress))

            robo_props = RoboProperties()
            difficulty = StvDifficulty.from_difficulty_code(diff_code, robo_props.num_of_qubits,
                                                            robo_props.circuit_space)
            self.__start_level_transition(self.__cur_map.name, ExpeditionMap.to_display_name(difficulty, rand_map_seed),
                                          lambda: self.__load_expedition(difficulty, rand_map_seed, rand_puzzle_seed))
        else:
            self.__start_level_transition(self.__cur_map.name, LevelInfo.convert_to_display_name(next_map),
                                          lambda: self.load_map(next_map, None, rand_map_seed))

    def __load_back(self):
        self.__exit_map()

    def __proceed(self, confirmed: int = 0):
        # not defined inside trigger_event() since it doesn't depend on any internal state of trigger_event() and,
        #  therefore, it's unnecessary to create __proceed again for every trigger_event()-call
        if confirmed == 0:
            self.__load_next()
        elif confirmed == 1:
            pass  # stay
        elif confirmed == 2:
            self.__load_back()

    def trigger_event(self, event_id: str):
        if event_id.lower() == MapConfig.done_event_id():
            # event_id = MapConfig.specific_done_event_id(self.__cur_map.internal_name)
            # self.__save_data.trigger_event(event_id)
            prev_level_data = self.__save_data.get_level_data(self.__cur_map.internal_name)
            duration, _ = time_diff(cur_datetime(), self.__level_timer)

            # store progress in save_data
            if self.is_in_level:
                new_level_data = self.__save_data.complete_level(
                    self.__cur_map.internal_name, duration, score=self.__cur_map.robot.score)
            elif self.is_in_expedition:
                assert isinstance(self.__cur_map, ExpeditionMap), \
                    f"CurMap has wrong type: \"{self.__cur_map.internal_name}\" is no ExpeditionMap!"
                new_level_data = self.__save_data.complete_expedition(
                    self.__cur_map.internal_name, duration, self.__cur_map.difficulty.level, self.__cur_map.main_gate,
                    score=self.__cur_map.robot.score)
            else:   # currently only levels and expedition can trigger done-events
                return

            self.__save_data.save(is_auto_save=True)    # persist the progress

            def show_end_message(end_message: Optional[Message]):
                def _show_proceed_summary():
                    CommonQuestions.proceed_summary(self.__cur_map.name, new_level_data.score, new_level_data.duration,
                                                    new_level_data.total_score, self.__proceed,
                                                    None if prev_level_data is None
                                                    else (prev_level_data.total_score, prev_level_data.duration))
                # either show the end message followed by the summary or just the summary
                if end_message is None: _show_proceed_summary()
                else: Popup.from_message_trigger(end_message, _show_proceed_summary)
            self.__cur_map.end(show_end_message)

        elif event_id.lower().startswith(MapConfig.unlock_prefix()):
            self.__save_data.unlock(event_id[len(MapConfig.unlock_prefix()):])
        else:
            if event_id in self.__temp_level_event_storage:  # todo: is score needed? a simple flag might be better
                event_score, event_done_score = self.__temp_level_event_storage[event_id]
                if event_score < event_done_score:
                    Config.check_reachability("MapManager.trigger_event() for existing event")
                    self.__temp_level_event_storage[event_id] = event_score + 1, event_done_score
            else:
                self.__temp_level_event_storage[event_id] = 1, 1

    def check_level_event(self, event: str) -> bool:
        """
        Used for popups to correctly display event-based messages.
        """
        if event in self.__temp_level_event_storage:
            score, done_score = self.__temp_level_event_storage[event]
            return score >= done_score
        return False

    def on_level_start(self):
        self.__temp_level_event_storage.clear()
        self.__level_timer = cur_datetime()

    def load_first_uncleared_map(self) -> None:
        seed = self.__rm.get_seed("MapManager.load_first_uncleared_map()")
        if Config.test_level(ignore_debugging=False):
            self.load_map(MapConfig.test_level(), None, seed)
        else:
            self.load_map(MapConfig.first_uncleared(), None, seed)

    def reload(self):
        if self.is_in_level:
            self.__load_level(self.__cur_map.internal_name, seed=None)     # set seed None to re-randomize it
        elif self.is_in_expedition:
            exp_map: ExpeditionMap = self.__cur_map
            # use same difficulty and map_seed but re-randomize puzzle_seed
            self.__load_expedition(exp_map.difficulty, exp_map.seed, None)
        else:
            Popup.error(f"Can only reload levels and expeditions, but the current map "
                        f"\"{self.__cur_map.internal_name}\" is neither. Please exit the map.", add_report_note=True)
