
from game.map.tiles import Tile


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
            raise Exception("This class is a singleton!")
        else:
            TileRenderer.__instance = self

    @staticmethod
    def render(tile: Tile):
        return tile.get_img()

