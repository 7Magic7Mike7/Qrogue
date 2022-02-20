from typing import Callable

from qrogue.dungeon_editor.dungeon_parser.QrogueLevelGenerator import QrogueLevelGenerator
from qrogue.game.actors.robot import Robot
from qrogue.game.callbacks import CallbackPack
from qrogue.game.map.generator import RandomDungeonGenerator
from qrogue.game.map.navigation import Coordinate
from qrogue.game.save_data import SaveData


class Expedition:
    def __init__(self, save_data: SaveData, load_map_callback: Callable[[str, Coordinate], None]):
        self.__save_data = save_data
        self.__load_map = load_map_callback
        self.__seed = self.__save_data.get_expedition_seed()
        self.__robot = None

    @property
    def _cbp(self) -> CallbackPack:
        return self.__save_data.cbp

    @property
    def _seed(self) -> int:
        return self.__seed

    @property
    def _robot(self) -> Robot:
        return self.__robot

    def set_robot(self, robot: Robot):
        self.__robot = robot

    def start(self) -> bool:
        test_mode = 0
        if test_mode == 0:
            generator = RandomDungeonGenerator(self._seed, self.__save_data, self.__load_map)
            map, success = generator.generate(self.__robot)
        elif test_mode == 1:
            generator = QrogueLevelGenerator(self._seed, self.__save_data, self.__load_map)
            map, success = generator.generate("tutorial")
        else:
            success = False
            #generator = QrogueWorldGenerator(self.__seed, aaaa)
            #text = PathConfig.read_world("worlds")
            #map, success = generator.generate(self.__robot, self.__cbp, text)

        if success:
            self._cbp.start_level(self._seed, map)
            return True
        else:
            return False

    def abort(self):
        pass
