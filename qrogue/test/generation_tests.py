import unittest
from typing import Optional, Any

import test_util
from qrogue.game.world.dungeon_generator import DungeonGenerator
from qrogue.game.world.dungeon_generator.random_generator import RandomLayoutGenerator, ExpeditionGenerator
from qrogue.management.save_data import SaveData
from qrogue.util import TestConfig

printing = False


class SingletonSetupTestCase(unittest.TestCase):
    @staticmethod
    def _print(msg: Optional[Any] = None, force: bool = False):
        if printing or force:
            print(msg)

    def setUp(self) -> None:
        TestConfig.activate()
        # now create new singletons
        if not test_util.init_singletons(include_config=True):
            raise Exception("Could not initialize singletons")
        SaveData()

    def tearDown(self) -> None:
        # first reset
        SaveData.reset()
        test_util.reset_singletons()


class LayoutGenTestCase(SingletonSetupTestCase):
    def test_layout(self):
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

            if not map_gen.check_special_rooms():
                wrong_specials_seeds.append(seed)
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


class LevelGenTestCase(SingletonSetupTestCase):
    def test_dungeon(self):
        start_seed = 0
        end_seed = 5
        failing_seeds = []

        i = 0
        for seed in range(start_seed, end_seed):
            if i % 1000 == 0:
                self._print(f"Run {i + 1}): seed = {seed}")
            generator = ExpeditionGenerator(seed, lambda s: True, lambda s: None, lambda s: None)
            map_, success = generator.generate(SaveData.instance().get_robot(0))
            if not success:
                failing_seeds.append((generator, seed))
                self._print(f"Failed for seed = {seed}")
            i += 1

        if len(failing_seeds) > 0:
            self.assert_(False, "Some seeds failed!")
            self._print("Failing Seeds:", force=True)
            seeds = []
            for mg, seed in failing_seeds:
                self._print(mg, force=True)
                seeds.append(seed)
            self._print(seeds, force=True)
            self._print(force=True)


if __name__ == '__main__':
    unittest.main()
