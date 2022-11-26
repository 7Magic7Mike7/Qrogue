import unittest

from qrogue.game.world.dungeon_generator.wave_function_collapse.wfc_generator import WFCRoomGenerator, \
    WFCLayoutGenerator
from qrogue.game.world.map.rooms import AreaType, DefinedWildRoom, Area
from qrogue.test import test_util
from qrogue.util import TestConfig, MapConfig
from qrogue.util.util_functions import enum_str


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_learner(self):
        pass

    def test_layout_generator(self):
        test_util.init_singletons(include_config=True)

        generator = WFCLayoutGenerator(7, [(level, True) for level in MapConfig.level_list()])
        for i in range(7):
            generator.start()
            level = generator.generate()
            text = ""
            for row in level:
                for val in row:
                    text += f"{enum_str(val)}  "
                text += "\n"
            print(text)
            print()

    def test_room_generator(self):
        test_util.init_singletons(include_config=True)

        generator = WFCRoomGenerator(7, [(level, True) for level in MapConfig.level_list()], room_type=AreaType.WildRoom)
        for i in range(7):
            generator.start()
            room = generator.generate()

            text = "#" * Area.UNIT_WIDTH + "\n"
            for row in room:
                text += "#"
                for val in row:
                    text += val.code.representation
                text += "#\n"
            text += "#" * Area.UNIT_WIDTH + "\n"
            print(text)
            print()

        #learner.remove_special_tiles()
        #print(learner)


if __name__ == '__main__':
    unittest.main()
