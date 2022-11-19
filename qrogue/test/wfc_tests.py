import unittest

from qrogue.game.world.dungeon_generator import WFCLayoutGenerator
from qrogue.test import test_util
from qrogue.util import TestConfig, MapConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_learner(self):
        pass

    def test_layout_generator(self):
        test_util.init_singletons(include_config=True)

        generator = WFCLayoutGenerator(7, [(level, True) for level in MapConfig.level_list()])
        generator.generate()
        print(generator)


if __name__ == '__main__':
    unittest.main()
