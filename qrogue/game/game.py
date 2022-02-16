
from qrogue.game.controls import Controls
from qrogue.util.logger import Logger
from qrogue.util.my_random import RandomManager
from qrogue.widgets.qrogue_pycui import QrogueCUI


class GameHandler:
    __instance = None

    @staticmethod
    def instance() -> "GameHandler":
        if GameHandler.__instance is None:
            Logger.instance().throw(Exception("This singleton has not been initialized yet!"))
        return GameHandler.__instance

    def __init__(self, seed: int):
        if GameHandler.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            GameHandler.__instance = self
            # create the singletons
            RandomManager(seed)
            Logger(seed)
            controls = Controls()   # todo load later from file!

            self.__renderer = QrogueCUI(seed, controls)

    def start(self) -> None:
        self.__renderer.start()
