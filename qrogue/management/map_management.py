from typing import Callable, Optional

from qrogue.game.world.dungeon_generator import ExpeditionGenerator, QrogueLevelGenerator, QrogueWorldGenerator
from qrogue.game.world.map import Map, WorldMap, MapType
from qrogue.game.world.navigation import Coordinate
from qrogue.management import StoryNarration
from qrogue.util import CommonQuestions, Config, Logger, MyRandom, MapConfig, achievements

from qrogue.management.save_data import SaveData


__MAP_ORDER = {
    MapConfig.spaceship(): MapConfig.intro_level(),
    MapConfig.intro_level(): "w1",  # "hacky" fix to the problem that the player might use quickstart instead of
                                    # navigation during MoonMission
    "l1v2": "l1v3",
    "l1v3": "l1v4",
    "l1v4": "w2",
}


def get_next(cur_level: str) -> str:
    if cur_level == MapConfig.spaceship():
        next_level = __MAP_ORDER[cur_level]
        while SaveData.instance().achievement_manager.check_achievement(next_level):
            if next_level in __MAP_ORDER:
                next_level = __MAP_ORDER[next_level]
            else:
                break
        return next_level
    elif cur_level in __MAP_ORDER:
        return __MAP_ORDER[cur_level]
    return None


class MapManager:
    __instance = None

    @staticmethod
    def instance() -> "MapManager":
        if MapManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return MapManager.__instance

    def __init__(self, seed: int, show_world: Callable[[Optional[WorldMap]], None],
                 start_level: Callable[[int, Map], None]):
        if MapManager.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            self.__rm = MyRandom(seed)
            self.__show_world = show_world
            self.__start_level = start_level
            self.__world_memory = {}    # str -> WorldMap

            generator = QrogueWorldGenerator(seed, SaveData.instance().player,
                                             SaveData.instance().achievement_manager.check_achievement,
                                             SaveData.instance().achievement_manager.add_to_achievement,
                                             self.__load_map)
            hub_world, success = generator.generate("worlds")
            if not success:
                Logger.instance().throw(RuntimeError("Unable to build world map! Please download again and make sure "
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

    def __get_world(self, level_name: str) -> WorldMap:
        if level_name[0] == "l" and level_name[1].isdigit():
            world_name = "w" + level_name[1]
            if world_name in self.__world_memory:
                return self.__world_memory[world_name]
            else:
                def trigger_achievement(name: str):
                    SaveData.instance().achievement_manager.add_to_achievement(name, 1)
                check_achievement = SaveData.instance().achievement_manager.check_achievement
                generator = QrogueWorldGenerator(self.__rm.get_seed(), SaveData.instance().player, check_achievement,
                                                 trigger_achievement, self.__load_map)
                world, success = generator.generate(world_name)
                if success:
                    self.__world_memory[world_name] = world
                    return world
                else:
                    Logger.instance().error(f"Error! Unable to build map \"{world_name}\". Returning to HubWorld")
        return self.__world_memory[MapConfig.hub_world()]

    def __load_map(self, map_name: str, room: Coordinate):
        if map_name == MapConfig.spaceship():
            next_map = get_next(MapConfig.spaceship())
            if next_map is None:
                next_map = MapConfig.hub_world()
            self.load_map(next_map, None)
        elif map_name in self.__world_memory:
            self.__cur_map = self.__world_memory[map_name]
            self.__in_level = False
            self.__show_world(self.__cur_map)
        elif map_name[0].lower().startswith(MapConfig.world_map_prefix()): # and map_name[1].isdigit():
            player = SaveData.instance().player
            check_achievement = SaveData.instance().achievement_manager.check_achievement
            trigger_event = self.trigger_level_event  # SaveData.instance().achievement_manager.trigger_level_event

            generator = QrogueWorldGenerator(self.__rm.get_seed(), player, check_achievement, trigger_event,
                                             self.__load_map)
            try:
                world, success = generator.generate(map_name)
                if success:
                    self.__cur_map = world
                    self.__in_level = False
                    self.__show_world(self.__cur_map)
                else:
                    Logger.instance().error(f"Could not load world \"{map_name}\"!")
            except FileNotFoundError:
                Logger.instance().error(f"Failed to open the specified world-file: {map_name}")
        elif map_name.lower().startswith(MapConfig.level_map_prefix()):
            # todo maybe levels should be able to have arbitrary names aside from "w..." or "back"?
            check_achievement = SaveData.instance().achievement_manager.check_achievement
            trigger_event = self.trigger_level_event
            generator = QrogueLevelGenerator(self.__rm.get_seed(), check_achievement, trigger_event, self.__load_map)
            try:
                level, success = generator.generate(map_name)
                if success:
                    self.__cur_map = level
                    self.__in_level = True
                    self.__start_level(self.__rm.get_seed(), self.__cur_map)
                else:
                    Logger.instance().error(f"Could not load level \"{map_name}\"!")
            except FileNotFoundError:
                Logger.instance().error(f"Failed to open the specified level-file: {map_name}")
        elif map_name.lower().startswith(MapConfig.expedition_map_prefix()):
            difficulty = int(map_name[len(MapConfig.expedition_map_prefix()):])
            seed = self.__rm.get_seed()
            robot = SaveData.instance().get_robot(0)
            check_achievement = SaveData.instance().achievement_manager.check_achievement
            trigger_event = self.trigger_level_event #SaveData.instance().achievement_manager.trigger_level_event
            generator = ExpeditionGenerator(seed, check_achievement, trigger_event, self.__load_map)
            expedition, success = generator.generate(robot)
            if success:
                self.__cur_map = expedition
                self.__in_level = True
                self.__start_level(seed, self.__cur_map)
            else:
                Logger.instance().error(f"Could not create expedition with seed = {seed}")
        elif map_name == MapConfig.back_map_string():
            self.__load_back()
        else:
            Logger.instance().error(f"Invalid map to load: {map_name}")

    def __load_next(self):
        next_map = get_next(self.__cur_map.internal_name)
        if next_map:
            self.load_map(next_map, None)
        else:
            world = self.__get_world(self.__cur_map.internal_name)
            self.__show_world(world)

    def __load_back(self):
        if self.__in_level:
            # if we are currently in a level we return to the current world
            self.__in_level = False
            self.__show_world(self.__get_world(self.__cur_map.internal_name))
        elif self.__cur_map is self.__hub_world or not StoryNarration.unlocked_free_navigation():
            # we return to the spaceship if we are currently in the hub-world or haven't unlocked it yet
            self.__show_world(None)
        else:
            # if we are currently in a world we return to the hub-world
            self.__cur_map = self.__hub_world
            self.__in_level = False
            self.__show_world(self.__cur_map)

    def __proceed(self, confirmed: bool = True):
        if confirmed:
            self.__load_next()

    def trigger_level_event(self, event_id: str):
        if event_id.lower() == MapConfig.done_event_id():
            event_id = MapConfig.specific_done_event_id(self.__cur_map.internal_name)
            if self.__cur_map.get_type() is MapType.World:
                SaveData.instance().achievement_manager.finished_world(self.__cur_map.internal_name)
            elif self.__cur_map.get_type() is MapType.Level:
                SaveData.instance().achievement_manager.finished_level(self.__cur_map.internal_name)
            elif self.__cur_map.get_type() is MapType.Expedition:
                SaveData.instance().achievement_manager.add_to_achievement(achievements.CompletedExpedition, 1)

            if self.__cur_map.internal_name == MapConfig.intro_level():
                self.__show_world(None)     # go back to the spaceship
            else:
                CommonQuestions.ProceedToNextMap.ask(self.__proceed)
        SaveData.instance().achievement_manager.trigger_level_event(event_id)
        if Config.debugging():
            print("triggered event: " + event_id)

    def load_map(self, map_name: str, spawn_room: Coordinate):
        if map_name.lower() == MapConfig.next_map_string():
            self.__load_next()
        else:
            self.__load_map(map_name, spawn_room)
