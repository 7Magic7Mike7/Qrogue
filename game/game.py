
from game.controls import Controls
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
            RandomManager(seed)
            Logger()    # create the logger

            self.__renderer = QrogueCUI(seed, Controls())

    def start(self):
        self.__renderer.start()
        self.__renderer.render()

    def stop(self):
        self.__renderer.stop()
