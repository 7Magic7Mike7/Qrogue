import unittest
from typing import List, Callable, Any, Tuple, Optional

from qrogue.game.logic.actors import Robot, BaseBot, Enemy, Boss, Riddle, Challenge
from qrogue.game.world.navigation import Direction
from qrogue.graphics import WidgetWrapper
from qrogue.graphics.widgets.my_widgets import SelectionWidget
from qrogue.management import SaveData
from qrogue.util import RandomManager, Config, PathConfig, Logger, Controls, TestConfig, CheatConfig


def true_callback() -> bool:
    return True


def false_callback() -> bool:
    return False


def start_gp(args):
    print("started game")


def start_fight(robot: Robot, enemy: Enemy, direction: Direction):
    pass


def start_boss_fight(robot: Robot, boss: Boss, direction: Direction):
    pass


def open_riddle(robot: Robot, riddle: Riddle):
    pass


def open_challenge(robot: Robot, challenge: Challenge):
    pass


def visit_shop(robot: Robot, items: List[ShopItem]):
    pass


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
    TestLogger()    # works since we access Logger only via .instance()
    #Logger.instance().info(Config.get_log_head(seed), from_pycui=False)
    Logger.instance().set_popup(error_popup)
    #CallbackPack(start_gp, start_fight, start_boss_fight, open_riddle, open_challenge, game_over)

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
