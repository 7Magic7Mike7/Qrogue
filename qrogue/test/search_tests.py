import unittest

from qrogue.game.world.dungeon_generator.path_search import Search
from qrogue.game.world.map import rooms
from qrogue.game.world.navigation import Coordinate
from qrogue.game.world.tiles import TileCode


class MyTestCase(unittest.TestCase):
    def test_weighted_obstacles(self):
        room = [
            [TileCode.Floor, TileCode.Floor, TileCode.Obstacle, TileCode.Obstacle, TileCode.Collectible],
            [TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Obstacle, TileCode.Obstacle],
            [TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor],
            [TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor],
            [TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor, TileCode.Floor],
        ]
        pos = Coordinate(rooms.Room.INNER_WIDTH-1, 0)   # top right corner

        def get_tile_code(coordinate: Coordinate) -> TileCode:
            return room[coordinate.y][coordinate.x]

        def is_goal(coordinate: Coordinate) -> bool:
            # North entrance
            if coordinate.x == rooms.Room.INNER_MID_X and coordinate.y == 0: return True
            # East entrance
            if coordinate.x == rooms.Room.INNER_WIDTH-1 and coordinate.y == rooms.Room.INNER_MID_Y: return True
            # South entrance
            if coordinate.x == rooms.Room.INNER_MID_X and coordinate.y == rooms.Room.INNER_HEIGHT-1: return True
            # West entrance
            if coordinate.x == 0 and coordinate.y == rooms.Room.INNER_MID_Y: return True

            return False

        weight_matrix = Search.get_weighted_obstacles_matrix(pos, get_tile_code)
        """
        for row in weight_matrix: print(row)
        print("#############")
        for row in room:
            print("#", end=" ")
            for tc in row:
                print(tc.representation, end=" ")
            print("#")
        print("#############")
        """

        path = Search.simple_room_visit(pos, lambda c: weight_matrix[c.y][c.x], is_goal)
        self.assertSequenceEqual([Coordinate(3, 0), Coordinate(4, 1), Coordinate(4, 2)], path,
                                 f"Wrong path: {print(' -> '.join([str(c) for c in path]))}")


if __name__ == '__main__':
    unittest.main()
