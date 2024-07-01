import unittest
from typing import List, Callable, Any, Tuple, Optional, Dict

from qrogue.game.logic.actors import BaseBot
from qrogue.graphics import WidgetWrapper
from qrogue.graphics.widgets.my_widgets import SelectionWidget
from qrogue.util import Logger, Controls, Config, PathConfig, TestConfig, CheatConfig, DifficultyType, StvDifficulty
from qrogue.util.util_functions import enum_string


def load_map(map_name: str):
    print(f"Load map: {map_name}")


def game_over():
    print("game over")


def message_popup(title: str, text: str, position: Optional[int] = None):
    print("----------------------------------------")
    print(f"[{title}]")
    print(text)
    print("----------------------------------------")


def error_popup(text: str):
    print("----------------------------------------")
    print(f"ERROR")
    print(text)
    print("----------------------------------------")


def handle_error(error: str):
    raise Exception(f"[ERROR] {error}")


def get_dummy_controls(activate_printing: bool = False) -> Controls:
    def handle_key_presses(key: int):
        if activate_printing:
            print(f"{key} was pressed")

    return Controls(handle_key_presses)


def init_singletons(include_config: bool = False, custom_data_path: Optional[str] = None,
                    custom_user_path: Optional[str] = None) -> bool:
    """

    :param include_config: whether to also load config or not
    :param custom_data_path: optional, if given uses the path to load game data
    :param custom_user_path: optional, if given uses the path to load and store user data
    :return: whether initialization was successful or not
    """
    if include_config:
        if PathConfig.load_paths(custom_data_path, custom_user_path):
            return_code = Config.load()
            if return_code != 0:
                print(f"Error #{return_code}")
                return False
            Config.activate_debugging()
        else:
            print("Error! Could not load base paths.")
            return False

    # initialize a special TestLogger instead of the normal Logger
    TestLogger()  # works since we access Logger only via .instance()
    # Logger.instance().info(Config.get_log_head(seed), from_pycui=False)
    Logger.instance().set_popup(error_popup)
    # CallbackPack(start_gp, start_fight, start_boss_fight, open_riddle, open_challenge, game_over)

    CheatConfig.init(lambda s0, s1, i0, i1: None, lambda s, i, c: None, True, True)

    return True


def reset_singletons():
    Logger.reset()


class TestLogger(Logger):
    __PRINT_PYCUI: bool = False

    @staticmethod
    def print_pycui(activate: bool = True):
        TestLogger.__print_pycui = activate

    def __init__(self):
        super().__init__(print)
        Logger._set_instance(self)

    def _write(self, text: str, from_pycui: Optional[bool]) -> None:
        # skip writing if text comes from PyCUI and we do not want to log PyCUI-messages
        if from_pycui is True and not TestLogger.__PRINT_PYCUI: return
        super()._write(text, from_pycui)


class SingletonSetupTestCase(unittest.TestCase):
    __printing: bool = False

    @staticmethod
    def set_printing(active: bool):
        SingletonSetupTestCase.__printing = active

    @staticmethod
    def _print(msg: Optional[Any] = None, force: bool = False):
        if SingletonSetupTestCase.__printing or force:
            print(msg)

    def setUp(self) -> None:
        TestConfig.activate()
        # now create new singletons
        if not init_singletons(include_config=True):
            raise Exception("Could not initialize singletons")

    def tearDown(self) -> None:
        # first reset
        reset_singletons()

    def test_singleton_setup(self):
        self.assertRaises(Exception, self.setUp, None)  # setups without an intermediate tearDown() should fail
        self.tearDown()     # tear down for next setup
        self.setUp()        # setup again to see if setups for multiple tests after another are correctly reset
        self.tearDown()     # tear down current setup
        self.tearDown()     # no error should happen when tearing down without intermediate setUp()
        self.setUp()        # setup for next tear down
        self.tearDown()     # tear down again so the final post-test tearDown fails if this is an issue


class DummyWidget(WidgetWrapper):
    def __init__(self):
        self.title = ""
        self.selected = False

    def get_pos(self) -> Tuple[int, int]:
        return 0, 0

    def get_abs_pos(self) -> Tuple[int, int]:
        return 0, 0

    def get_size(self) -> Tuple[int, int]:
        return 1, 1

    def get_abs_size(self) -> Tuple[int, int]:
        return 1, 1

    def is_selected(self):
        return self.selected

    def reposition(self, row: int = None, column: int = None, row_span: int = None, column_span: int = None):
        pass

    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = None, include_whitespace: bool = False, selected_color=None) -> None:
        pass

    def reset_text_color_rules(self) -> None:
        pass

    def activate_individual_coloring(self):
        pass

    def add_key_command(self, keys: List[int], command: Callable[[], Any], overwrite: bool = True) -> Any:
        pass

    def set_title(self, title: str) -> None:
        self.title = title

    def get_title(self) -> str:
        return self.title

    def toggle_border(self):
        pass


class DummySelectionWidget(SelectionWidget):
    def __init__(self, columns: int, is_second: bool = False, stay_selected: bool = False, print_keys: bool = False):
        self.__dummy_widget = DummyWidget()
        super(DummySelectionWidget, self).__init__(self.__dummy_widget, get_dummy_controls(print_keys), columns,
                                                   is_second, stay_selected)

    def get_dummy_widget(self) -> DummyWidget:
        return self.__dummy_widget

    def up(self):
        self._up()

    def right(self):
        self._right()

    def down(self):
        self._down()

    def left(self):
        self._left()


class DummyRobot(BaseBot):
    def __init__(self):
        super(DummyRobot, self).__init__(game_over)

    def get_img(self):
        return "D"

    def description(self, check_unlocks: Optional[Callable[[str], bool]] = None) -> str:
        return "Minimal Robot for testing non-Robot dependent code (e.g. tiles)."


class ExplicitStvDifficulty(StvDifficulty):
    @staticmethod
    def compute_relative_value(diff_type: DifficultyType, diff_dict: Dict[DifficultyType, int], num_of_qubits: int,
                               circuit_space: int) -> float:
        if diff_type in diff_dict:
            abs_val = diff_dict[diff_type]
        else:
            raise Exception(f"No value defined for {enum_string(diff_type)}!")

        if diff_type is DifficultyType.CircuitExuberance:
            return abs_val / circuit_space
        if diff_type is DifficultyType.QubitExuberance:
            return abs_val / num_of_qubits
        if diff_type is DifficultyType.RotationExuberance:
            return abs_val / StvDifficulty._compute_absolute_value(DifficultyType.QubitExuberance, diff_dict,
                                                                   num_of_qubits, circuit_space, None)
        if diff_type is DifficultyType.RandomizationDegree:
            return abs_val
        if diff_type is DifficultyType.BonusEditRatio:
            return abs_val / StvDifficulty._compute_absolute_value(DifficultyType.CircuitExuberance, diff_dict,
                                                                   num_of_qubits, circuit_space, None)
        raise NotImplementedError(f"No relative value computation implemented for {enum_string(diff_type)}")

    @staticmethod
    def _get_closes_level(diff_type: DifficultyType, value: float) -> int:
        """
        Compute which level has its value closest to the given value.
        """
        closest_level = StvDifficulty.min_difficulty_level()
        closest_delta = abs(StvDifficulty._get_diff_value(diff_type, closest_level) - value)
        for i in range(1, StvDifficulty.num_of_difficulty_levels()):
            cur_level = i + StvDifficulty.min_difficulty_level()
            cur_delta = abs(StvDifficulty._get_diff_value(diff_type, cur_level) - value)
            if cur_delta < closest_delta:
                closest_level = cur_level
                closest_delta = cur_delta
        return closest_level

    def __init__(self, values: Dict[DifficultyType, int], num_of_qubits: int, circuit_space: int):
        self.__values = values
        self.__num_of_qubits = num_of_qubits
        self.__circuit_space = circuit_space

        # approximate the levels based on relative values
        unknown_diff_levels: List[DifficultyType] = []
        level_values: Dict[DifficultyType, int] = {}
        for diff_type in DifficultyType:
            if diff_type in values:
                rel_val = ExplicitStvDifficulty.compute_relative_value(diff_type, values, num_of_qubits, circuit_space)
                level_values[diff_type] = ExplicitStvDifficulty._get_closes_level(diff_type, rel_val)
            else:
                unknown_diff_levels.append(diff_type)
        # fill in the missing level values based on the average level of the computed level values
        avg_level = StvDifficulty._calc_avg_level(level_values)
        for diff_type in unknown_diff_levels:
            level_values[diff_type] = avg_level

        # fill in the missing absolute values based on the average level
        # 1) approximate the relative values, so we can then compute the absolute values based on them
        rel_diff_dict: Dict[DifficultyType, float] = {}
        for diff_type, level in level_values.items():
            rel_diff_dict[diff_type] = StvDifficulty._get_diff_value(diff_type, level)
        # 2) compute the missing absolute values
        for diff_type in DifficultyType:
            if diff_type in values: continue
            fallback_value = StvDifficulty._get_diff_value(diff_type, avg_level)
            values[diff_type] = StvDifficulty._compute_absolute_value(diff_type, rel_diff_dict, num_of_qubits,
                                                                      circuit_space, fallback_value)

        super().__init__(level_values)

    def get_relative_value(self, diff_type: DifficultyType) -> float:
        diff_dict = {}
        for diff_type in DifficultyType:
            diff_dict[diff_type] = self.get_absolute_value(diff_type)
        return ExplicitStvDifficulty.compute_relative_value(diff_type, diff_dict, self.__num_of_qubits,
                                                            self.__circuit_space)

    def get_absolute_value(self, diff_type: DifficultyType, num_of_qubits: Optional[int] = None,
                           circuit_space: Optional[int] = None) -> int:
        if num_of_qubits is not None:
            assert num_of_qubits == self.__num_of_qubits, \
                f"Wrong number of qubits: {num_of_qubits} != {self.__num_of_qubits}!"
        if circuit_space is not None:
            assert circuit_space == self.__circuit_space, \
                f"Wrong circuit space: {circuit_space} != {self.__circuit_space}!"
        return self.__values[diff_type]

    def get_absolute_dict(self, num_of_qubits: Optional[int] = None,  circuit_space: Optional[int] = None) \
            -> Dict[DifficultyType, int]:
        if num_of_qubits is not None:
            assert num_of_qubits == self.__num_of_qubits, \
                f"Wrong number of qubits: {num_of_qubits} != {self.__num_of_qubits}!"
        if circuit_space is not None:
            assert circuit_space == self.__circuit_space, \
                f"Wrong circuit space: {circuit_space} != {self.__circuit_space}!"
        return self.__values.copy()

    def to_code(self) -> str:
        raise Exception("Invalid state: Cannot call to_code() for ExplicitStvDifficulty")

    def __str__(self):
        return f"ExplicitStvDifficulty{super().to_code()}"  # don't use self.to_code() since it's not supported
