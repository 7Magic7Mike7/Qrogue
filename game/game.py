
from game.controls import Controls
from util.key_logger import KeyLogger
from util.logger import Logger
from util.my_random import RandomManager
from widgets.qrogue_pycui import QrogueCUI


class GameHandler:
    __instance = None

    @staticmethod
    def instance() -> "GameHandler":
        if GameHandler.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return GameHandler.__instance

    def __init__(self, seed: int):
        if GameHandler.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GameHandler.__instance = self
            # create the singletons
            RandomManager(seed)
            Logger(seed)
            KeyLogger()
            controls = Controls()   # todo load later from file!

            self.__renderer = QrogueCUI(seed, controls)

    def start(self) -> None:
        self.__renderer.start()
