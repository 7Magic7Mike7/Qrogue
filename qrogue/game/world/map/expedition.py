"""
from typing import Callable

from qrogue.game.callbacks import CallbackPack
from qrogue.game.map import RandomDungeonGenerator
from qrogue.game.navigation import Coordinate


class Expedition:
    def __init__(self, seed: int, load_map_callback: Callable[[str, Coordinate], None]):
        self.__seed = seed
        self.__load_map = load_map_callback
        self.__robot = None

    def start(self) -> bool:
        generator = RandomDungeonGenerator(self.__seed, self.__load_map)
        expedition, success = generator.generate(self.__robot)

        if success:
            CallbackPack.instance().start_level(self.__seed, expedition)
            return True
        else:
            return False

    def abort(self):
        pass
"""