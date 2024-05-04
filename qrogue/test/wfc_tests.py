import unittest
from typing import Dict

from qrogue.game.world.dungeon_generator.wave_function_collapse import WaveFunction
from qrogue.game.world.dungeon_generator.wave_function_collapse.wfc_generator import WFCRoomGenerator, \
    WFCLayoutGenerator
from qrogue.game.world.map import AreaType, Area
from qrogue.test import test_util
from qrogue.util import MapConfig, RandomManager, TestConfig
from qrogue.util.util_functions import enum_str


class WFCGeneratorTestCases(test_util.SingletonSetupTestCase):
    def test_layout_generator(self):
        generator = WFCLayoutGenerator([(level, True) for level in MapConfig.level_list()])
        for i in range(7):
            level = generator.generate(7)
            text = ""
            for row in level:
                for val in row:
                    text += f"{enum_str(val)}  "
                text += "\n"
            self._print(text)
            self._print()

    def test_room_generator(self):
        generator = WFCRoomGenerator([(level, True) for level in MapConfig.level_list()],
                                     room_type=AreaType.WildRoom)
        for i in range(7):
            room = generator.generate(7)

            text = "#" * Area.UNIT_WIDTH + "\n"
            for row in room:
                text += "#"
                for val in row:
                    text += val.code.representation
                text += "#\n"
            text += "#" * Area.UNIT_WIDTH + "\n"
            self._print(text)
            self._print()


class WaveFunctionTestCase(test_util.SingletonSetupTestCase):
    def test_collapse_validity(self):
        rm = RandomManager.create_new(TestConfig.test_seed())

        tries_per_config = 100_000
        for sample_size in [10, 100, 1_000, 10_000]:
            for num_of_types in [2, 3, 4, 7, 10, 23, 100]:
                weights: Dict[int, int] = {}
                for key in range(num_of_types):
                    weights[key] = rm.get_int(0, sample_size)

                for _ in range(tries_per_config):
                    wave = WaveFunction(weights)
                    self.assertFalse(wave.is_collapsed, "WaveFunction collapsed before collapse()-call!")

                    val = wave.collapse(rm)
                    self.assertTrue(wave.is_collapsed, "WaveFunction did not collapse in collapse()-call!")

                    # check validity of collapse
                    self.assertNotEqual(val, None, "WaveFunction collapsed to None!")
                    self.assertTrue(isinstance(val, int), "WaveFunction collapsed to wrong data type!")
                    self.assertEqual(val, wave.state, "WaveFunction state is inconsistent!")
                    self.assertEqual(wave.state, wave.collapse(rm), "Second collapse didn't return wave.state!")

    def test_uniform_probabilities(self):
        rm = RandomManager.create_new(TestConfig.test_seed())

        tries_per_config = 100_000
        error_acceptance = 0.1
        for sample_size in [10, 100, 1_000, 10_000]:
            for num_of_types in [2, 3, 4, 7, 10, 23, 100]:
                weights: Dict[int, int] = {}
                counter: Dict[int, int] = {}
                for key in range(num_of_types):
                    weights[key] = sample_size
                    counter[key] = 0

                for _ in range(tries_per_config):
                    wave = WaveFunction(weights)
                    val = wave.collapse(rm)
                    counter[val] += 1

                mean_count = tries_per_config / num_of_types
                min_count = mean_count * (1 - error_acceptance)
                max_count = mean_count * (1 + error_acceptance)
                for key in counter:
                    self.assertTrue(min_count <= counter[key] <= max_count,
                                    f"counter[{key}] = {counter[key]} is not close enough to {mean_count}")

    def test_force_value(self):
        rm = RandomManager.create_new(TestConfig.test_seed())

        wave = WaveFunction({1: 3, 2: 4})
        self.assertTrue(wave.force_value(7), "Failed to force integer value onto integer WaveFunction!")

        wave = WaveFunction({1: 3, 2: 4})
        wave.collapse(rm)
        self.assertRaises(AssertionError, wave.force_value, 7)

        wave = WaveFunction({1: 3, 2: 4})
        self.assertFalse(wave.force_value("str"), "Forced a string value onto integer WaveFunction!")

    def test_adapt_weights(self):
        print("TODO")


if __name__ == '__main__':
    unittest.main()
