from abc import ABC, abstractmethod
from typing import Tuple, Optional

from qrogue.game.world.map import Map
from qrogue.util import MapConfig


class DungeonGenerator(ABC):
    WIDTH = MapConfig.map_width()
    HEIGHT = MapConfig.map_height()

    def __init__(self, seed: int, width: int = WIDTH, height: int = HEIGHT):
        self.__seed = seed
        self._width = width
        self._height = height

    @property
    def seed(self) -> int:
        return self.__seed

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @abstractmethod
    def generate(self, data) -> Tuple[Optional[Map], bool]:
        pass
