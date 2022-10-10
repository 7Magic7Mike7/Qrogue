from enum import Enum
from typing import Callable, Tuple, List, Dict, Any

from qrogue.util.config import TestConfig, PopupConfig, PyCuiColors


class MapConfig:
    @staticmethod
    def num_of_lessons() -> int:
        return 8  # Lesson 0 to 7

    @staticmethod
    def map_width() -> int:
        return 7

    @staticmethod
    def map_height() -> int:
        return 3

    @staticmethod
    def room_width() -> int:
        return 7

    @staticmethod
    def room_height() -> int:
        return MapConfig.room_width()

    @staticmethod
    def room_mid_x() -> int:
        return int(MapConfig.room_width() / 2)

    @staticmethod
    def room_mid_y() -> int:
        return int(MapConfig.room_height() / 2)

    @staticmethod
    def room_mid() -> Tuple[int, int]:
        return MapConfig.room_mid_x(), MapConfig.room_mid_y()

    @staticmethod
    def done_event_id() -> str:
        return "done"

    @staticmethod
    def specific_done_event_id(completed_map: str) -> str:
        return f"{completed_map}{MapConfig.done_event_id()}"

    @staticmethod
    def global_event_prefix() -> str:
        return "global_event_"

    @staticmethod
    def next_map_string() -> str:
        return "next"

    @staticmethod
    def back_map_string() -> str:
        return "back"

    @staticmethod
    def world_map_prefix() -> str:
        return "w"

    @staticmethod
    def level_map_prefix() -> str:
        return "l"

    @staticmethod
    def expedition_map_prefix() -> str:
        return "expedition"

    @staticmethod
    def tutorial_lesson_prefix() -> str:
        return "l0v"

    @staticmethod
    def first_uncleared() -> str:
        return "firstUncleared"

    @staticmethod
    def spaceship() -> str:
        return "spaceship"

    @staticmethod
    def hub_world() -> str:
        return "worlds"

    @staticmethod
    def tutorial_world() -> str:
        return "w0"

    @staticmethod
    def first_world() -> str:
        return "w1"

    @staticmethod
    def intro_level() -> str:
        return f"{MapConfig.tutorial_lesson_prefix()}0"

    @staticmethod
    def exam() -> str:
        return "l0exam"

    @staticmethod
    def test_level() -> str:
        return "l0training"


class CheatConfig:
    __ALL = "aLL"
    __GOD_MODE = "Qod-Mode"
    __SCARED_RABBIT = "Rabbit_Tunnel"
    __INF_RESOURCES = "Rich"
    __MAP_REVEAL = "Illuminati"
    __OBSTACLE_IGNORE = "Obstacle-Iqnor"
    __NONE = "n0n3"
    __CHEATS = {
        __GOD_MODE: False,
        __SCARED_RABBIT: False,
        __INF_RESOURCES: False,
        __MAP_REVEAL: False,
        __OBSTACLE_IGNORE: False,
    }

    __allow_cheats = False
    __cheated = False
    __popup = None
    __input_popup = None

    @staticmethod
    def init(popup_callback: Callable[[str, str, int, int], None],
             input_popup_callback: Callable[[str, int, Callable[[str], None]], None], deactivate_cheats: bool = True,
             allow_cheats: bool = False):
        CheatConfig.__allow_cheats = allow_cheats
        CheatConfig.__cheated = False
        CheatConfig.__popup = popup_callback
        CheatConfig.__input_popup = input_popup_callback
        # deactivate cheats if we are not debugging
        if deactivate_cheats:
            for key in CheatConfig.__CHEATS:
                CheatConfig.__CHEATS[key] = False

    @staticmethod
    def did_cheat() -> bool:
        return CheatConfig.__cheated

    @staticmethod
    def in_god_mode() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__GOD_MODE]

    @staticmethod
    def is_scared_rabbit() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__SCARED_RABBIT]

    @staticmethod
    def got_inf_resources() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__INF_RESOURCES]

    @staticmethod
    def revealed_map() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__MAP_REVEAL]

    @staticmethod
    def ignore_obstacles() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__OBSTACLE_IGNORE]

    @staticmethod
    def cheat_input():
        if CheatConfig.__allow_cheats and CheatConfig.__input_popup is not None:
            CheatConfig.__input_popup("Input your Cheat:", PyCuiColors.BLACK_ON_RED, CheatConfig.__use_cheat)

    @staticmethod
    def cheat_list():
        text = ""
        for key in CheatConfig.__CHEATS:
            text += f"{key}: \t\t"
            if CheatConfig.__CHEATS[key]:
                text += "Active\n"
            else:
                text += "Inactive\n"
        CheatConfig.__popup("List of Cheats", text, PopupConfig.default_pos(), PopupConfig.default_color())

    @staticmethod
    def __use_cheat(code: str) -> bool:
        ret = False
        if code == CheatConfig.__ALL or code == CheatConfig.__NONE:
            for key in CheatConfig.__CHEATS:
                CheatConfig.__CHEATS[key] = code == CheatConfig.__ALL
            ret = True
        elif code in CheatConfig.__CHEATS:
            CheatConfig.__CHEATS[code] = not CheatConfig.__CHEATS[code]
            ret = True

        if ret:
            CheatConfig.__popup("Cheats", f"Successfully used the Cheat \"{code}\"", PopupConfig.default_pos(),
                                PopupConfig.default_color())
            CheatConfig.__cheated = True
        else:
            CheatConfig.__popup("Cheats", "This is not a valid Cheat!", PopupConfig.default_pos(),
                                PopupConfig.default_color())
        return ret


def _get_boolean_callback() -> Tuple[Callable[[int], str], Callable[[str], bool]]:
    def get(index: int) -> str:
        if index % 2 == 1:
            return "yes"
        else:
            return "no"

    def convert(value: str) -> bool:
        if value.lower() == "yes":
            return True
        else:
            return False
    return get, convert


def _get_float_callback(min_: float, max_: float, steps: int) -> Tuple[Callable[[int], str], Callable[[str], float]]:
    assert min_ < max_
    assert steps > 0
    range_ = max_ - min_
    step_size = range_ / steps

    def get(index: int) -> str:
        val = min_ + step_size * index
        return str(val)
    return get, float


class Options(Enum):
    auto_save = ("Auto Save", _get_boolean_callback(), 2, 1,
                 "Whether to automatically save the game on exit or not.")
    auto_reset_circuit = ("Auto Reset Circuit", _get_boolean_callback(), 2, 1,
                          "Automatically reset your Circuit to a clean state at the beginning of a Puzzle, Riddle, "
                          "etc.")
    log_keys = ("Log Keys", _get_boolean_callback(), 2, 1,
                "Stores all keys you pressed in a .qrkl-file so one can replay them (e.g. for analysing a bug)")

    gameplay_key_pause = ("Gameplay Key Pause", _get_float_callback(0.1, 1.0, 9), 9, 0,
                          "How long to wait before we process the next input during gameplay.")
    simulation_key_pause = ("Simulation Key Pause", _get_float_callback(0.05, 1.0, 19), 19, 3,
                            "How long to wait before we process the next input during simulation.")

    show_ket_notation = ("Show Ket-Notation", _get_boolean_callback(), 2, 1,
                         "Whether to display ket-notation for state vectors and circuit matrix or not.")
    allow_implicit_removal = ("Allow implicit Removal", _get_boolean_callback(), 2, 0,
                              "Allows you to place a gate on an occupied spot, removing the occupying gate in the "
                              "process.")
    allow_multi_move = ("Allow multi move", _get_boolean_callback(), 2, 0,
                        "Allows you to move multiple tiles at once by pressing a number followed by a direction.")
    auto_skip_text_animation = ("Auto skip text animation", _get_boolean_callback(), 2, 0,
                                "During some special scene transitions there will be some animated text describing "
                                "what happened in-between story sections. Skipping this means that the whole text "
                                "will be shown at once.")

    def __init__(self, name: str, get_value: Tuple[Callable[[int], str], Callable[[str], Any]], num_of_values: int,
                 default_index: int, description: str):
        self.__name = name
        self.__get_value, self.__convert_value = get_value
        self.__num_of_values = num_of_values
        self.__default_index = default_index
        self.__description = description

    @property
    def name(self) -> str:
        return self.__name

    @property
    def num_of_values(self) -> int:
        return self.__num_of_values

    @property
    def default_index(self) -> int:
        return self.__default_index

    @property
    def description(self) -> str:
        return self.__description

    def get_value(self, cur_index: int) -> str:
        return self.__get_value(cur_index)

    def convert(self, cur_index: int) -> Any:
        value = self.get_value(cur_index)
        return self.__convert_value(value)


class GameplayConfig:
    __KEY_VALUE_SEPARATOR = "="
    __OPTIONS: Dict[Options, int] = {
        Options.auto_save: Options.auto_save.default_index,
        Options.auto_reset_circuit: Options.auto_reset_circuit.default_index,
        Options.log_keys: Options.log_keys.default_index,

        Options.gameplay_key_pause: Options.gameplay_key_pause.default_index,
        Options.simulation_key_pause: Options.simulation_key_pause.default_index,

        Options.show_ket_notation: Options.show_ket_notation.default_index,
        Options.allow_implicit_removal: Options.allow_implicit_removal.default_index,

        Options.allow_multi_move: Options.allow_multi_move.default_index,
        Options.auto_skip_text_animation: Options.auto_skip_text_animation.default_index
    }

    @staticmethod
    def get_options() -> List[Tuple[Options, Callable[[Options], str]]]:
        """

        :return: list of [Option, Function to proceed to next value] for all gameplay config options
        """
        def next_(option: Options) -> str:
            # first increment the current index
            next_index = GameplayConfig.__OPTIONS[option] + 1
            if next_index >= option.num_of_values:
                next_index = 0
            GameplayConfig.__OPTIONS[option] = next_index
            # then return the corresponding new value
            return option.get_value(next_index)
        return [(option, next_) for option in GameplayConfig.__OPTIONS]

    @staticmethod
    def get_option_value(option: Options, convert: bool = True) -> Any:
        cur_index = GameplayConfig.__OPTIONS[option]
        if convert:
            if Options.simulation_key_pause and TestConfig.is_active():
                return TestConfig.key_pause()
            return option.convert(cur_index)
        else:
            return option.get_value(cur_index)

    @staticmethod
    def to_file_text() -> str:
        text = ""
        for option in GameplayConfig.__OPTIONS:
            cur_index = GameplayConfig.__OPTIONS[option]
            text += f"{option.name}{GameplayConfig.__KEY_VALUE_SEPARATOR}{cur_index}"
            text += "\n"
        return text

    @staticmethod
    def from_log_text(log_text: str) -> bool:
        def normalize(text: str) -> str:
            return text.lower().strip(" ")

        for line in log_text.splitlines():
            if len(line.strip(" ")) == 0:
                continue
            try:
                name, index = line.split(GameplayConfig.__KEY_VALUE_SEPARATOR)
                name = normalize(name)
                for val in Options.__members__.values():
                    if normalize(val.name) == name:     # compare the normalized names
                        GameplayConfig.__OPTIONS[val] = int(index)
                        break
            except IndexError:
                return False
            except KeyError:
                return False
        return True

    @staticmethod
    def auto_save() -> bool:
        return GameplayConfig.get_option_value(Options.auto_save, convert=True)

    @staticmethod
    def auto_reset_circuit() -> bool:
        return GameplayConfig.get_option_value(Options.auto_reset_circuit, convert=True)

    @staticmethod
    def log_keys() -> bool:
        return GameplayConfig.get_option_value(Options.log_keys, convert=True)


class PuzzleConfig:
    @staticmethod
    def calculate_appearance_chance(eid: int) -> float:
        return 0.1 * (10 - eid)   # the lower the id the higher the chance of a puzzle to appear

    @staticmethod
    def calculate_flee_chance(eid: int) -> float:
        return PuzzleConfig.calculate_appearance_chance(eid)

    @staticmethod
    def calculate_flee_energy(eid: int) -> int:
        return max(1, eid * 2)


class QuantumSimulationConfig:
    DECIMALS = 3
    TOLERANCE = 0.1
    MAX_SPACE_PER_NUMBER = 1 + 1 + 1 + DECIMALS  # sign + "0" + "." + DECIMALS
    MAX_PERCENTAGE_SPACE = 3


class ShopConfig:
    @staticmethod
    def base_unit() -> int:
        return 1


class InstructionConfig:
    MAX_ABBREVIATION_LEN = 3
