import unittest
from typing import Optional, Any

import test_util
from qrogue.game.world.dungeon_generator import DungeonGenerator
from qrogue.game.world.dungeon_generator.random_generator import RandomLayoutGenerator, ExpeditionGenerator
from qrogue.management.save_data import SaveData
from qrogue.util import ErrorConfig


printing = False


class MyTestCase(unittest.TestCase):
    def __init(self):
        try:
            if not test_util.init_singletons(include_config=True):
                raise Exception("Could not initialize singletons")
        except Exception as ex:
            if ex.args[0] != ErrorConfig.singleton():
                raise ex

        try:
            SaveData()
        except Exception as ex:
            if ex.args[0] != ErrorConfig.singleton():
                raise ex

    def __print(self, msg: Optional[Any] = None, force: bool = False):
        if printing or force:
            print(msg)

    def test_layout(self):
        self.__init()
        start_seed = 50000
        end_seed = 50005
        failing_seeds = []
        wrong_specials_seeds = []

        i = 0
        for seed in range(start_seed, end_seed):
            if i % 5000 == 0:
                self.__print(f"Run {i + 1}): seed = {seed}")
            map_gen = RandomLayoutGenerator(seed, DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
            if not map_gen.generate(debug=False):
                failing_seeds.append(map_gen)

            if not map_gen.check_special_rooms():
                wrong_specials_seeds.append(seed)
            i += 1

        if len(failing_seeds) > 0:
            self.__print("Failing Seeds:")
            seeds = []
            for mg in failing_seeds:
                seeds.append(mg.seed)
            self.__print(seeds)
            self.assert_(False, "Layout for some seeds failed!")

        if len(wrong_specials_seeds) > 0:
            self.__print("Wrong SpecialRooms in Seeds: ")
            self.__print(wrong_specials_seeds)
            self.__print()

    def test_dungeon(self):
        self.__init()
        start_seed = 0
        end_seed = 5
        failing_seeds = []

        i = 0
        for seed in range(start_seed, end_seed):
            if i % 1000 == 0:
                self.__print(f"Run {i + 1}): seed = {seed}")
            generator = ExpeditionGenerator(seed, lambda s: True, lambda s: None, lambda s: None)
            map_, success = generator.generate(SaveData.instance().get_robot(0))
            if not success:
                failing_seeds.append((generator, seed))
                self.__print(f"Failed for seed = {seed}")
            i += 1

        if len(failing_seeds) > 0:
            self.assert_(False, "Some seeds failed!")
            self.__print("Failing Seeds:", force=True)
            seeds = []
            for mg, seed in failing_seeds:
                self.__print(mg, force=True)
                seeds.append(seed)
            self.__print(seeds, force=True)
            self.__print(force=True)


if __name__ == '__main__':
    printing = False
    unittest.main()
