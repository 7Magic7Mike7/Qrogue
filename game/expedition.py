from dungeon_editor.parser.QrogueGrammarListener import TextBasedDungeonGenerator
from game.actors.robot import Robot
from game.callbacks import CallbackPack
from game.map.generator import RandomDungeonGenerator
from util.config import PathConfig


class Expedition:
    def __init__(self, cbp: CallbackPack):
        self.__cbp = cbp
        self.__seed = None
        self.__robot = None

    @property
    def _cbp(self) -> CallbackPack:
        return self.__cbp

    @property
    def _seed(self) -> int:
        return self.__seed

    @property
    def _robot(self) -> Robot:
        return self.__robot

    def set_seed(self, seed: int):
        self.__seed = seed

    def set_robot(self, robot: Robot):
        self.__robot = robot

    def start(self) -> bool:
        #generator = RandomDungeonGenerator(self.__seed)
        #map, success = generator.generate(self.__robot, self.__cbp, None)
        generator = TextBasedDungeonGenerator(self.__seed)
        text = PathConfig.read_dungeon("example1")
        map, success = generator.generate(self.__robot, self.__cbp, text)
        if success:
            self.__cbp.start_gameplay(self.__seed, self.__robot, map)
            return True
        else:
            return False
