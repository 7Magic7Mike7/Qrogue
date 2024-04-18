import time
from threading import Thread
from typing import Callable, Optional, Dict, List, Tuple

from qrogue.game.logic.actors import Robot
from qrogue.game.world.dungeon_generator import ExpeditionGenerator, QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import Map, MapType, ExpeditionMap, CallbackPack
from qrogue.game.world.navigation import Coordinate
from qrogue.graphics.popups import Popup
from qrogue.util import CommonQuestions, Logger, MapConfig, achievements, RandomManager, Config, \
    ErrorConfig, PathConfig

from qrogue.management.save_data import NewSaveData
from qrogue.util.achievements import Unlocks
from qrogue.util.level_info import LevelInfo
from qrogue.util.config.gameplay_config import ExpeditionConfig, GameplayConfig
from qrogue.util.util_functions import cur_datetime, time_diff


class MapManager:
    def __init__(self, save_data: NewSaveData, seed: int, start_level: Callable[[Map], None],
                 start_level_transition_callback: Callable[[str, str, Callable[[], None]], None],
                 exit_map_callback: Callable[[], None], callback_pack: CallbackPack, robot: Robot,
                 queue_size: int = ExpeditionConfig.DEFAULT_QUEUE_SIZE):
        self.__save_data = save_data
        # no longer used code!
        self.__exit_map = exit_map_callback
        self.__cbp = callback_pack
        self.__robot = robot
        self.__queue_size = queue_size

        self.__rm = RandomManager.create_new(seed)
        self.__start_level = start_level
        self.__start_level_transition = start_level_transition_callback
        self.__expedition_generator = ExpeditionGenerator(seed,
                                                          self.__save_data.check_achievement,
                                                          self.__trigger_event, self.load_map, callback_pack)
        self.__expedition_queue: List[ExpeditionMap] = []
        self.__cur_map: Map = None
        self.__in_level = False

        self.__level_timer = cur_datetime()
        self.__temp_level_event_storage: Dict[str, Tuple[int, int]] = {}  # event name -> score, done_score

    @property
    def in_level(self) -> bool:
        return self.__in_level

    @property
    def in_expedition(self) -> bool:
        return self.__cur_map.get_type() is MapType.Expedition

    @property
    def show_individual_qubits(self) -> bool:
        return self.__cur_map.show_individual_qubits

    def fill_expedition_queue(self, callback: Optional[Callable[[], None]] = None, no_thread: bool = False):
        if len(self.__expedition_queue) >= self.__queue_size:
            return

        def fill():
            robot = self.__robot
            while len(self.__expedition_queue) < self.__queue_size:
                expedition, success = self.__expedition_generator.generate(self.__rm.get_seed(), robot)
                if success:
                    self.__expedition_queue.append(expedition)

            if callback is not None:
                callback()
        if no_thread:
            fill()
        else:
            Thread(target=fill, args=(), daemon=True).start()

    def load_map(self, map_name: str, spawn_room: Optional[Coordinate], map_seed: Optional[int] = None):
        if map_name == MapConfig.first_uncleared():
            next_map = LevelInfo.get_next(MapConfig.spaceship(), self.__save_data.check_level)   # todo: get rid of .spaceship()
            if next_map is None:
                self.load_map(MapConfig.hub_world(), spawn_room, map_seed)
            else:
                self.load_map(next_map, spawn_room, map_seed)

        elif map_name.lower() == MapConfig.next_map_string():
            self.__load_next()

        elif map_name.lower() == MapConfig.back_map_string():
            self.__load_back()

        elif map_name == MapConfig.spaceship():
            ErrorConfig.raise_deletion_exception()

        elif map_name.lower().startswith(MapConfig.world_map_prefix()):
            ErrorConfig.raise_deletion_exception()

        elif map_name.lower().startswith(MapConfig.level_map_prefix()):
            if map_seed is None:
                map_seed = self.__rm.get_seed(msg="MapMngr_seedForLevel")

            # todo maybe levels should be able to have arbitrary names except "w..." or "e..." or "back" or "next"?
            check_achievement = self.__save_data.check_achievement
            generator = QrogueLevelGenerator(map_seed, check_achievement, self.__trigger_event, self.load_map,
                                             Popup.npc_says, self.__cbp)
            try:
                level, success = generator.generate(map_seed, map_name)
                if success:
                    self.__cur_map = level
                    self.__in_level = True
                    self.__start_level(self.__cur_map)
                else:
                    Popup.error(f"Failed to generate level \"{map_name}\"!", add_report_note=True)
            except FileNotFoundError:
                Popup.error(f"Level-file for \"{map_name}\" was not found! Please download the game files again.\n"
                            f"If this error still occurs but you're sure that the corresponding file is present:",
                            add_report_note=True)

        elif map_name.lower().startswith(MapConfig.expedition_map_prefix()):
            if len(map_name) > len(MapConfig.expedition_map_prefix()):
                # difficulty = int(map_name[len(MapConfig.expedition_map_prefix()):])
                map_seed = int(map_name[len(MapConfig.expedition_map_prefix()):])
            else:
                # difficulty = ExpeditionConfig.DEFAULT_DIFFICULTY
                map_seed = None

            robot = self.__robot
            if map_seed is None and self.__queue_size > 0:
                while len(self.__expedition_queue) <= 0:
                    time.sleep(Config.loading_refresh_time())
                success = True
                expedition = self.__expedition_queue.pop(0)
                self.fill_expedition_queue()
            else:
                if map_seed is None:
                    map_seed = self.__rm.get_seed()
                expedition, success = self.__expedition_generator.generate(map_seed, robot)

            if success:
                robot.reset()
                self.__cur_map = expedition
                self.__in_level = True
                self.__start_level(map_seed, self.__cur_map)
            else:
                Popup.error(f"Failed to create an expedition for seed = {map_seed}. Please try again with a different "
                            f"seed or restart the game. Should the error keep occurring:", add_report_note=True)

        else:
            Popup.error(f"Failed to recognize \"{map_name}\" as map. Please download the game files again.\n"
                        f"If this error still occurs but you're sure that the corresponding file is present:",
                        add_report_note=True)

    def __load_next(self):
        next_map = LevelInfo.get_next(self.__cur_map.internal_name, self.__save_data.check_level)
        if next_map:
            next_display = LevelInfo.convert_to_display_name(next_map)
            self.__start_level_transition(self.__cur_map.name, next_display, lambda: self.load_map(next_map, None, None))
        else:
            ErrorConfig.raise_deletion_exception()

    def __load_back(self):
        if self.__cur_map.get_type() == MapType.Expedition:
            ErrorConfig.raise_deletion_exception()
        elif self.__in_level:
            self.__in_level = False
            self.__exit_map()
        else:
            ErrorConfig.raise_deletion_exception()

    def __proceed(self, confirmed: int = 0):
        if confirmed == 0:
            self.__load_next()
        elif confirmed == 1:
            pass    # stay
        elif confirmed == 2:
            self.__load_back()

    def __trigger_event(self, event_id: str):
        if event_id.lower() == MapConfig.done_event_id():
            #event_id = MapConfig.specific_done_event_id(self.__cur_map.internal_name)
            #self.__save_data.trigger_event(event_id)
            prev_level_data = self.__save_data.get_level_data(self.__cur_map.internal_name)
            duration, _ = time_diff(cur_datetime(), self.__level_timer)
            new_level_data = self.__save_data.complete_level(self.__cur_map.internal_name, duration,
                                                             score=self.__cur_map.robot.score)

            if self.__cur_map.get_type() is MapType.Expedition:
                self.__save_data.add_to_achievement(achievements.CompletedExpedition, 1)    # todo: add score instead of 1?
            elif self.__cur_map.get_type() is MapType.Level:
                pass
            else:
                ErrorConfig.raise_deletion_exception()
            self.__save_data.save(is_auto_save=True)

            CommonQuestions.proceed_summary(self.__cur_map.name, new_level_data.score, new_level_data.duration,
                                            new_level_data.total_score, self.__proceed,
                                            None if prev_level_data is None
                                            else (prev_level_data.total_score, prev_level_data.duration))

            #if self.__save_data.check_unlocks(Unlocks.ProceedChoice):
            #    CommonQuestions.ProceedToNextMap.ask(self.__proceed)    # todo: ask only if we are currently replaying the level (if no proceed, go back to hub)
            #else:
            #    self.__proceed()
        else:
            if event_id in self.__temp_level_event_storage:     # todo: is score needed? a simple flag might be better
                event_score, event_done_score = self.__temp_level_event_storage[event_id]
                if event_score < event_done_score:
                    Config.check_reachability("MapManager.__trigger_event() for existing event")
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
        if Config.test_level(ignore_debugging=False):
            self.load_map(MapConfig.test_level(), None)
        else:
            map_name = LevelInfo.get_next(MapConfig.first_uncleared(), self.__save_data.check_level)
            self.load_map(map_name, None)

    def load_expedition(self, seed: Optional[int] = None) -> None:
        self.load_map(MapConfig.expedition_map_prefix(), None, seed)

    def reload(self):
        self.load_map(self.__cur_map.internal_name, None, self.__cur_map.seed)
