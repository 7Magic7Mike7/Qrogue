import unittest

import test_util
from qrogue.game.world.dungeon_generator import DungeonGenerator
from qrogue.game.world.dungeon_generator.random_generator import RandomLayoutGenerator, ExpeditionGenerator
from qrogue.game.world.map import Room
from qrogue.game.world.map.rooms import Hallway
from qrogue.game.world.navigation import Direction, Coordinate
from qrogue.game.world import tiles
from qrogue.management.save_data import NewSaveData
from qrogue.util import CheatConfig


class LayoutGenTestCase(test_util.SingletonSetupTestCase):
    def test_single_seed(self):
        seed = 297
        map_gen = RandomLayoutGenerator(seed, DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
        self.assertTrue(map_gen.generate(debug=False), "Failed to generate!")
        self.assertTrue(map_gen.validate(), f"Invalid layout: {map_gen}")
        self._print(map_gen)

    def test_layout(self):
        # took ~10 seconds for seeds 50_000 to 55_000, succeeded
        # ~3:20 min for 0 to 100_000, succeeded
        start_seed = 50000
        end_seed = 50005
        failing_seeds = []
        wrong_specials_seeds = []

        i = 0
        for seed in range(start_seed, end_seed):
            if i % 5000 == 0:
                self._print(f"Run {i + 1}): seed = {seed}")
            map_gen = RandomLayoutGenerator(seed, DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
            if not map_gen.generate(debug=False):
                failing_seeds.append(map_gen)
            self.assertTrue(map_gen.validate(), f"Invalid layout: {map_gen}")
            i += 1

        if len(failing_seeds) > 0:
            self._print("Failing Seeds:")
            seeds = []
            for mg in failing_seeds:
                seeds.append(mg.seed)
            self._print(seeds)
            self.assert_(False, "Layout for some seeds failed!")

        if len(wrong_specials_seeds) > 0:
            self._print("Wrong SpecialRooms in Seeds: ")
            self._print(wrong_specials_seeds)
            self._print()


class LevelGenTestCase(test_util.SingletonSetupTestCase):
    def test_single_seed(self):
        CheatConfig.use_cheat("Illuminati")
        generator = ExpeditionGenerator(0, lambda s: True, lambda s: None, lambda s: None)
        seed = 297
        map_, success = generator.generate((NewSaveData().get_robot(0), seed))
        self.assertTrue(success, "Failed to generate.")
        self._print(map_)

    def test_expedition(self):
        # ~1min per 666 seeds
        # 1_000 seeds per ~1.5min
        start_seed = 0
        end_seed = 5
        failing_seeds = []

        generator = ExpeditionGenerator(0, lambda s: True, lambda s: None, lambda s: None)
        for i, seed in enumerate(range(start_seed, end_seed)):
            if i % 1000 == 0:
                self._print(f"Run {i + 1}): seed = {seed}")
            map_, success = generator.generate((NewSaveData().get_robot(0), seed))
            if not success:
                failing_seeds.append((generator, seed))
                self._print(f"Failed for seed = {seed}")

        if len(failing_seeds) > 0:
            self._print("Failing Seeds:", force=True)
            seeds = []
            for mg, seed in failing_seeds:
                self._print(mg, force=True)
                seeds.append(seed)
            self._print(seeds, force=True)
            self._print(force=True)
            self.assertTrue(False, "Some seeds failed!")

    def test_room_correction(self):
        tile_list = Room.dic_to_tile_list({
            Coordinate(3, 0): tiles.Obstacle(),
            Coordinate(4, 0): tiles.Obstacle(),

            Coordinate(0, 1): tiles.Obstacle(),
            Coordinate(1, 1): tiles.Obstacle(),
            Coordinate(2, 1): tiles.Obstacle(),
            Coordinate(3, 1): tiles.Obstacle(),
            Coordinate(4, 1): tiles.Obstacle(),

            Coordinate(0, 2): tiles.Obstacle(),
            Coordinate(1, 2): tiles.Obstacle(),
            Coordinate(2, 2): tiles.Obstacle(),

            Coordinate(1, 3): tiles.Obstacle(),
            Coordinate(2, 3): tiles.Obstacle(),
            Coordinate(3, 3): tiles.Obstacle(),

            Coordinate(2, 4): tiles.Obstacle(),
            Coordinate(4, 4): tiles.Obstacle(),
        })
        hallways = {
            Direction.North: Hallway(tiles.Door(Direction.North)),
            Direction.South: Hallway(tiles.Door(Direction.South)),
        }
        """
        print("Before correction:")
        before_room = DefinedWildRoom(tile_list, north_hallway=hallways[Direction.North], south_hallway=hallways[Direction.South])
        print(before_room.to_string())
        """
        num_of_changes = ExpeditionGenerator.correct_tile_list(tile_list, hallways)
        self.assertGreater(num_of_changes, -1, "Could not correct the given tile_list!")
        """
        print("After correction:")
        after_room = DefinedWildRoom(tile_list, north_hallway=hallways[Direction.North],
                                     south_hallway=hallways[Direction.South])
        print(after_room.to_string())
        """

    def test_astar(self):
        tile_dic = {
            Coordinate(0, 2): tiles.Obstacle(),
            Coordinate(1, 2): tiles.Obstacle(),
            Coordinate(2, 2): tiles.Obstacle(),
            Coordinate(3, 2): tiles.Obstacle(),
            Coordinate(4, 2): tiles.Obstacle(),
            Coordinate(4, 3): tiles.Obstacle(),
        }
        tile_list = Room.dic_to_tile_list(tile_dic)

        def get_weight(pos: Coordinate) -> int:
            if pos in tile_dic:
                return 2
            if pos.x == 2 and pos.y in [0, 4]:
                # one of the entrances
                return 0
            return 1

        visited = set()
        success, tiles_to_remove = ExpeditionGenerator.path_search(tile_list,
                                                                   lambda t: t.code == tiles.TileCode.Obstacle,
                                                                   get_weight, visited, target_pos=Coordinate(2, 4),
                                                                   cur_pos=Coordinate(2, 0))
        self.assertTrue(success, "Didn't find a removable tile.")
        """
        print([str(elem) for elem in tiles_to_remove])
        visited = list(visited)
        visited.sort(key=lambda c: c.x + c.y * 10)
        print(f"Visited: {[str(elem) for elem in visited]}")
        """


if __name__ == '__main__':
    unittest.main()
