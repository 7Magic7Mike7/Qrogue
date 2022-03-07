from typing import Callable, Optional

from qrogue.dungeon_editor.dungeon_parser.QrogueLevelGenerator import QrogueLevelGenerator
from qrogue.dungeon_editor.world_parser.QrogueWorldGenerator import QrogueWorldGenerator
from qrogue.game.map.generator import RandomDungeonGenerator
from qrogue.game.map.level_map import LevelMap
from qrogue.game.map.navigation import Coordinate
from qrogue.game.map.world_map import WorldMap
from qrogue.game.save_data import SaveData
from qrogue.util.config import Config
from qrogue.util.logger import Logger
from qrogue.util.my_random import MyRandom


__MAP_ORDER = {
    "l1v1": "l1v2",
    "l1v2": "l1v3",
    "l1v3": "l1v4",
    "l1v4": "w2",
}


def get_next(cur_level: str) -> str:
    if cur_level in __MAP_ORDER:
        return __MAP_ORDER[cur_level]
    return None


class MapManager:
    HUB_WORLD_NAME = "w0"
    __instance = None

    @staticmethod
    def instance() -> "MapManager":
        if MapManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return MapManager.__instance

    def __init__(self, seed: int, show_world: Callable[[Optional[WorldMap]], None],
                 start_level: Callable[[int, LevelMap], None]):
        if MapManager.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            self.__rm = MyRandom(seed)
            self.__show_world = show_world
            self.__start_level = start_level
            self.__world_memory = {}    # str -> WorldMap

            generator = QrogueWorldGenerator(seed, SaveData.instance(), self.__load_map)
            hub_world, success = generator.generate("worlds")
            if not success:
                Logger.instance().throw(RuntimeError("Unable to build world map! Please download again and make sure "
                                                     "to not edit game data."))
            self.__world_memory[self.HUB_WORLD_NAME] = hub_world
            self.__cur_map = hub_world
            self.__in_level = False

            MapManager.__instance = self

    @property
    def __hub_world(self) -> WorldMap:
        return self.__get_world(self.HUB_WORLD_NAME)

    def __get_world(self, level_name: str) -> WorldMap:
        if level_name[0] == "l" and level_name[1].isdigit():
            world_name = "w" + level_name[1]
            if world_name in self.__world_memory:
                return self.__world_memory[world_name]
            else:
                generator = QrogueWorldGenerator(self.__rm.get_seed(), SaveData.instance(), self.__load_map)
                world, success = generator.generate("worlds")
                if success:
                    self.__world_memory[world_name] = world
                    return world
                else:
                    Logger.instance().error(f"Error! Unable to build map \"{world_name}\". Returning to HubWorld")
        return self.__world_memory[self.HUB_WORLD_NAME]

    def __load_map(self, map_name: str, room: Coordinate):
        if map_name[0].lower() == "w" and map_name[1].isdigit():
            if map_name in self.__world_memory:
                self.__show_world(self.__world_memory[map_name])
            else:
                generator = QrogueWorldGenerator(self.__rm.get_seed(), SaveData.instance(), self.__load_map)
                try:
                    world, success = generator.generate(map_name)
                    if success:
                        self.__cur_map = world
                        self.__show_world(world)
                    else:
                        Logger.instance().error(f"Could not load world \"{map_name}\"!")
                except FileNotFoundError:
                    Logger.instance().error(f"Failed to open the specified world-file: {map_name}")
        elif map_name[0].lower() == "l":
            # todo maybe levels should be able to have arbitrary names aside from "w..." or "back"?
            generator = QrogueLevelGenerator(self.__rm.get_seed(), SaveData.instance(), self.__load_map)
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
        elif map_name.lower() == "expedition":
            seed = self.__rm.get_seed()
            generator = RandomDungeonGenerator(seed, SaveData.instance(), self.__load_map)
            expedition, success = generator.generate(SaveData.instance().get_robot(0))
            if success:
                self.__cur_map = expedition
                self.__in_level = True
                self.__start_level(seed, self.__cur_map)
            else:
                Logger.instance().error(f"Could not create expedition with seed = {seed}")
        elif map_name == Config.back_map_string():
            if self.__in_level:
                # if we are currently in a level we return to the current world
                self.__in_level = False
                self.__show_world(self.__get_world(self.__cur_map.name))
            elif self.__cur_map == self.__hub_world:
                # if we are currently in the hub-world we return to the spaceship
                self.__show_world(None)
            else:
                # if we are currently in a world we return to the hub-world
                self.__show_world(self.__hub_world)
                self.__cur_map = self.__hub_world
        else:
            Logger.instance().error(f"Invalid map to load: {map_name}")

    def load_map(self, map_name: str, spawn_room: Coordinate):
        if map_name.lower() == "next":  # todo handle magic string
            self.load_next()
        else:
            self.__load_map(map_name, spawn_room)

    def load_next(self):
        next_map = get_next(self.__cur_map.name)
        if next_map:
            self.load_map(next_map, None)
        else:
            world = self.__get_world(self.__cur_map.name)
            self.__show_world(world)
