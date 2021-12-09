
from game.map.tiles import Tile
from util.logger import Logger


class TileRenderer:
    __instance = None

    @staticmethod
    def instance() -> "TileRenderer":
        if TileRenderer.__instance is None:
            TileRenderer()
        return TileRenderer.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if TileRenderer.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            TileRenderer.__instance = self

    @staticmethod
    def render(tile: Tile):
        return tile.get_img()

