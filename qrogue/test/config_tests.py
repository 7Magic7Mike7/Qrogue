import unittest
from typing import Dict, Any

from qrogue.test.test_util import SingletonSetupTestCase
from qrogue.util import GameplayConfig, Options, OptionsManager, ScoreConfig


class MyOptionsTest(SingletonSetupTestCase):
    @staticmethod
    def _default_options_text() -> str:
        return """
Energy Mode=0
Auto Save=1
Auto Reset Circuit=1
Log Keys=1
Gameplay Key Pause=0.1
Simulation Key Pause=0.2
Show Ket-Notation=1
Allow implicit Removal=0
Allow multi move=0
Auto skip text animation=0
Enable puzzle history=1
Auto reset history=1
"""

    @staticmethod
    def _default_option_values() -> Dict[Options, Any]:
        values = {}
        for option in Options:
            values[option] = option.get_value(option.default_index)
        return values

    @staticmethod
    def __obt(val: bool) -> bool:
        """
        :returns: option value is bool True
        """
        return val is True

    @staticmethod
    def __oft(val: float) -> bool:
        """
        :returns: option value is float True
        """
        return val == 1

    @staticmethod
    def __ost(val: str) -> bool:
        """
        :returns: option value is str True
        """
        return val.lower() in ["yes", "y", "true"]

    @staticmethod
    def _are_options_values_equal(val1: Any, val2: Any) -> bool:
        if val1 == val2: return True

        if isinstance(val1, bool):
            if isinstance(val2, float):
                return MyOptionsTest.__obt(val1) == MyOptionsTest.__oft(val2)
            if isinstance(val2, str):
                return MyOptionsTest.__obt(val1) == MyOptionsTest.__ost(val2)
            return False

        elif isinstance(val1, float):
            if isinstance(val2, bool):
                return MyOptionsTest.__oft(val1) == MyOptionsTest.__obt(val2)
            if isinstance(val2, str):
                return MyOptionsTest.__oft(val1) == MyOptionsTest.__ost(val2)

        elif isinstance(val1, str):
            if isinstance(val2, bool):
                return MyOptionsTest.__ost(val1) == MyOptionsTest.__obt(val2)
            if isinstance(val2, float):
                return MyOptionsTest.__ost(val1) == MyOptionsTest.__oft(val2)

        return False

    def setUp(self) -> None:
        super().setUp()

    def test_text_import(self):
        options_text = MyOptionsTest._default_options_text()
        options_values = MyOptionsTest._default_option_values()

        self.assertTrue(OptionsManager.from_text(options_text), "Failed to load GameplayConfig")

        for option in Options:
            exp_val = options_values[option]
            # ignore since we want the real value, not a value potentially adapted by tests
            act_val = GameplayConfig.get_option_value(option, ignore_test_config=True)
            self.assertTrue(MyOptionsTest._are_options_values_equal(exp_val, act_val),
                            f"Non-equal value for Option={option.name}: expected \"{exp_val}\" but got \"{act_val}\"")


class ScoreTest(unittest.TestCase):
    def testTimeBonus(self):
        score_bounds = 100, 1000, 10_000, 100_000
        score_steps = 20, 100, 2000
        dur_bounds = 20, 200, 400, 1000, 10_000
        dur_steps = 5, 10, 20, 100
        for i, sc_step in enumerate(score_steps):
            for j, dur_step in enumerate(dur_steps):
                for score in range(score_bounds[i], score_bounds[i+1], sc_step):
                    for dur in range(dur_bounds[j], dur_bounds[j+1], dur_step):
                        bonus = ScoreConfig.compute_time_bonus(score, dur)
                        self.assertGreaterEqual(bonus, 0)


if __name__ == '__main__':
    unittest.main()
