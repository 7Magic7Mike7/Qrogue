
from qrogue.util import Logger, RandomManager

from qrogue.management.qrogue_pycui import QrogueCUI


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

            self.__renderer = QrogueCUI(seed)

    def start(self) -> None:
        self.__renderer.start()
