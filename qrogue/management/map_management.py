from typing import Callable, Optional, Dict

from qrogue.game.world.dungeon_generator import ExpeditionGenerator, QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import Map, WorldMap, MapType
from qrogue.game.world.navigation import Coordinate
from qrogue.graphics.popups import Popup
from qrogue.util import CommonQuestions, Logger, MapConfig, achievements, RandomManager, Config, TestConfig

from qrogue.management.save_data import SaveData
from qrogue.util.achievements import Ach, Unlocks
from qrogue.util.config.gameplay_config import ExpeditionConfig

__MAP_ORDER = {
    #MapConfig.spaceship(): MapConfig.intro_level(),
    MapConfig.first_uncleared(): MapConfig.intro_level(),
    MapConfig.intro_level(): "l0v1",
    "l0v1": "l0v2",
    "l0v2": "l0v3",
    "l0v3": "l0v4",
    "l0v4": "l0v5",
    "l0v5": "l0v6",
    "l0v6": "l0v7",
    "l0v7": "w0",
    "l0training": "w0",
    "l0exam": MapConfig.spaceship(),
    "w0": MapConfig.spaceship(),

    MapConfig.hub_world(): "l0v0",
}


def get_next(cur_map: str) -> Optional[str]:
    if cur_map == MapConfig.first_uncleared():
        next_map = __MAP_ORDER[cur_map]
        while SaveData.instance().achievement_manager.check_achievement(next_map):
            if next_map in __MAP_ORDER:
                next_map = __MAP_ORDER[next_map]
            else:
                break
        return next_map
    elif cur_map in __MAP_ORDER:
        return __MAP_ORDER[cur_map]
    return None


class MapManager:
    __instance = None

    @staticmethod
    def instance() -> "MapManager":
        if MapManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return MapManager.__instance

    @staticmethod
    def reset():
        if TestConfig.is_active():
            MapManager.__instance = None
        else:
            raise TestConfig.StateException("Can only reset the singleton \"MapManager\" during testing!")

    def __init__(self, seed: int, show_world: Callable[[Optional[WorldMap]], None],
                 start_level: Callable[[int, Map], None]):
        if MapManager.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            self.__base_seed = seed
            self.__rm = RandomManager.create_new(seed)
            self.__show_world = show_world
            self.__start_level = start_level
            self.__world_memory: Dict[str, WorldMap] = {}    # str -> WorldMap

            generator = QrogueWorldGenerator(seed, SaveData.instance().player,
                                             SaveData.instance().achievement_manager.check_achievement,
                                             SaveData.instance().achievement_manager.add_to_achievement,
                                             self.load_map, Popup.npc_says)
            hub_world, success = generator.generate(MapConfig.hub_world())
            if not success:
                Logger.instance().throw(RuntimeError("Unable to build hub world! Please download again and make sure "
                                                     "to not edit game data."))
            self.__world_memory[MapConfig.hub_world()] = hub_world
            self.__cur_map = hub_world
            self.__in_level = False

            MapManager.__instance = self

    @property
    def __hub_world(self) -> WorldMap:
        return self.__get_world(MapConfig.hub_world())

    @property
    def in_hub_world(self) -> bool:
        return self.__cur_map is self.__hub_world

    @property
    def in_level(self) -> bool:
        return self.__cur_map.get_type() is MapType.Level

    def __show_spaceship(self):
        self.__show_world(None)

    def get_restart_message(self) -> str:
        # todo maybe should be handled differently. I'm not satisfied by this approach but for now it works and is
        #  straight forward.
        if self.__get_world(self.__cur_map.internal_name).internal_name == MapConfig.tutorial_world():
            return "Do you want to restart the current lesson?"
        else:
            return "Connection lost..."

    def __load_world(self, world_name: str) -> Optional[WorldMap]:
        """
        Loads the world either from memory or generates it from its file. In case of generation the world's achievement
        score will also be corrected.

        :param world_name: internal name of the world to load
        :return: a WorldMap corresponding to the provided name or None if it could not be generated
        """
        if world_name in self.__world_memory:
            return self.__world_memory[world_name]

        generator = QrogueWorldGenerator(self.__base_seed, SaveData.instance().player,
                                         SaveData.instance().achievement_manager.check_achievement,
                                         SaveData.instance().achievement_manager.add_to_achievement,
                                         self.load_map, Popup.npc_says)
        world, success = generator.generate(world_name)
        if success:
            level_counter = 0
            for level in world.mandatory_level_iterator():
                if SaveData.instance().achievement_manager.check_achievement(level):
                    level_counter += 1
            SaveData.instance().achievement_manager.correct_world_progress(world.internal_name, level_counter,
                                                                           world.num_of_mandatory_levels)
            self.__world_memory[world_name] = world
            return world
        else:
            return None

    def __get_world(self, level_name: str) -> WorldMap:
        if level_name[0] == "l" and level_name[1].isdigit():
            world_name = "w" + level_name[1]
            world = self.__load_world(world_name)
            if world is None:
                Logger.instance().error(f"Error! Unable to build map \"{world_name}\". Returning to HubWorld",
                                        from_pycui=False)
            else:
                return world
        return self.__world_memory[MapConfig.hub_world()]

    def __load_map(self, map_name: str, room: Optional[Coordinate], map_seed: Optional[int] = None):
        if map_name == MapConfig.first_uncleared():
            next_map = get_next(MapConfig.spaceship())
            if next_map is None:
                self.__load_map(MapConfig.hub_world(), room, map_seed)
            else:
                self.__load_map(next_map, room, map_seed)

        elif map_name == MapConfig.spaceship():
            self.__show_spaceship()

        elif map_name in self.__world_memory:
            self.__cur_map = self.__world_memory[map_name]
            self.__in_level = False
            self.__show_world(self.__cur_map)

        elif map_name[0].lower().startswith(MapConfig.world_map_prefix()):
            try:
                world = self.__load_world(map_name)
                if world is not None:
                    self.__cur_map = world
                    self.__in_level = False
                    self.__show_world(self.__cur_map)
                else:
                    Logger.instance().error(f"Could not load world \"{map_name}\"!", from_pycui=False)
            except FileNotFoundError:
                Logger.instance().error(f"Failed to open the specified world-file: {map_name}", from_pycui=False)

        elif map_name.lower().startswith(MapConfig.level_map_prefix()):
            if map_seed is None:
                map_seed = self.__rm.get_seed(msg="MapMngr_seedForLevel")

            # todo maybe levels should be able to have arbitrary names except "w..." or "e..." or "back" or "next"?
            check_achievement = SaveData.instance().achievement_manager.check_achievement
            generator = QrogueLevelGenerator(map_seed, check_achievement, self.__trigger_event, self.load_map,
                                             Popup.npc_says)
            try:
                level, success = generator.generate(map_name)
                if success:
                    self.__get_world(level.internal_name)
                    self.__cur_map = level
                    self.__in_level = True
                    self.__start_level(map_seed, self.__cur_map)
                else:
                    Logger.instance().error(f"Could not load level \"{map_name}\"!", from_pycui=False)
            except FileNotFoundError:
                Logger.instance().error(f"Failed to open the specified level-file: {map_name}", from_pycui=False)

        elif map_name.lower().startswith(MapConfig.expedition_map_prefix()):
            if map_seed is None:
                map_seed = self.__rm.get_seed(msg="MapMngr_seedForExpedition")

            if len(map_name) > len(MapConfig.expedition_map_prefix()):
                difficulty = int(map_name[len(MapConfig.expedition_map_prefix()):])
            else:
                difficulty = ExpeditionConfig.DEFAULT_DIFFICULTY
            robot = SaveData.instance().get_robot(0)
            check_achievement = SaveData.instance().achievement_manager.check_achievement
            generator = ExpeditionGenerator(map_seed, check_achievement, self.__trigger_event, self.load_map)
            expedition, success = generator.generate(robot)
            if success:
                robot.reset()
                self.__cur_map = expedition
                self.__in_level = True
                self.__start_level(map_seed, self.__cur_map)
            else:
                Logger.instance().error(f"Could not create expedition with seed = {map_seed}", from_pycui=False)

        elif map_name == MapConfig.back_map_string():
            self.__load_back()
        else:
            Logger.instance().error(f"Invalid map to load: {map_name}", from_pycui=False)

    def __load_next(self):
        next_map = get_next(self.__cur_map.internal_name)
        if next_map:
            self.__load_map(next_map, None, None)
        else:
            world = self.__get_world(self.__cur_map.internal_name)
            self.__show_world(world)

    def __load_back(self):
        if self.__cur_map.get_type() == MapType.Expedition:
            self.__show_spaceship()     # todo for now every expedition returns to the spaceship
        elif self.__in_level:
            # if we are currently in a level we return to the current world
            self.__in_level = False
            self.__show_world(self.__get_world(self.__cur_map.internal_name))
        elif self.__cur_map is self.__hub_world or \
                not Ach.check_unlocks(Unlocks.FreeNavigation, SaveData.instance().story_progress):
            # we return to the default world if we are currently in the hub-world or haven't unlocked it yet
            self.__show_world(None)
        else:
            # if we are currently in a world we return to the hub-world
            self.__cur_map = self.__hub_world
            self.__in_level = False
            self.__show_world(self.__cur_map)

    def __proceed(self, confirmed: int = 0):
        if confirmed == 0:
            self.__load_next()
        elif confirmed == 1:
            pass    # stay
        elif confirmed == 2:
            self.__load_back()

    def __trigger_event(self, event_id: str):
        if event_id.lower() == MapConfig.done_event_id():
            event_id = MapConfig.specific_done_event_id(self.__cur_map.internal_name)
            SaveData.instance().achievement_manager.trigger_event(event_id)

            if self.__cur_map.get_type() is MapType.World:
                SaveData.instance().achievement_manager.finished_world(self.__cur_map.internal_name)
            elif self.__cur_map.get_type() is MapType.Level:
                if SaveData.instance().achievement_manager.finished_level(self.__cur_map.internal_name,
                                                                          self.__cur_map.name):
                    # if the level was not finished before, we may increase the score of the world's achievement
                    world = self.__get_world(self.__cur_map.internal_name)
                    if world.is_mandatory_level(self.__cur_map.internal_name):
                        SaveData.instance().achievement_manager.add_to_achievement(world.internal_name, 1.0)

            elif self.__cur_map.get_type() is MapType.Expedition:
                SaveData.instance().achievement_manager.add_to_achievement(achievements.CompletedExpedition, 1)

            if Ach.check_unlocks(Unlocks.ProceedChoice, SaveData.instance().story_progress):
                CommonQuestions.ProceedToNextMap.ask(self.__proceed)
            else:
                self.__proceed()
        else:
            SaveData.instance().achievement_manager.trigger_event(event_id)

    def load_map(self, map_name: str, spawn_room: Optional[Coordinate], map_seed: Optional[int] = None):
        if map_name.lower() == MapConfig.next_map_string():
            self.__load_next()
        elif map_name.lower() == MapConfig.back_map_string():
            self.__load_back()
        else:
            self.__load_map(map_name, spawn_room, map_seed)

    def load_first_uncleared_map(self) -> None:
        if Config.test_level(ignore_debugging=False):
            self.__load_map(MapConfig.test_level(), None)
        else:
            map_name = get_next(MapConfig.first_uncleared())
            self.__load_map(map_name, None)

    def reload(self):
        self.__load_map(self.__cur_map.internal_name, None, self.__cur_map.seed)
