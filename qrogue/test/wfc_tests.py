import unittest

from qrogue.game.world.map.rooms import AreaType
from qrogue.test import test_util
from qrogue.util import TestConfig, MapConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_learner(self):
        pass

    def test_layout_generator(self):
        test_util.init_singletons(include_config=True)

        #generator = WFCLayoutGenerator(7, [(level, True) for level in MapConfig.level_list()])
        #generator.generate()
        #print(generator)

    def test_room_learner(self):
        test_util.init_singletons(include_config=True)

        pos_weights = {}
        type_weights = {}
        #learner = WFCRoomLearner(AreaType.WildRoom, pos_weights, type_weights)
        #generator = QrogueLevelGenerator(7, lambda s: True, lambda: None, lambda s, c: None, lambda s0, s1: None)

        for data in [(level, True) for level in MapConfig.level_list()]:
            level_name, in_dungeon_folder = data
            #level_map, success = generator.generate(level_name, in_dungeon_folder)
            #if success:
            #    learner.learn(LearnableLevelMap(level_map))

        #learner.remove_special_tiles()
        #print(learner)


if __name__ == '__main__':
    unittest.main()
