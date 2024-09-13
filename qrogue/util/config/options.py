from enum import Enum
from typing import Dict, Optional, List, Callable, Tuple, Any

from .test_config import TestConfig


class OptionsType(Enum):
    Bool = 0
    Float = 1

    def get_callbacks(self, data: Any) -> Tuple[Callable[[int], str], Callable[[str], Any]]:
        if self is OptionsType.Bool:
            return OptionsType._get_boolean_callback()
        elif self is OptionsType.Float:
            if isinstance(data, Tuple) and len(data) == 3:
                min_, max_, steps = data
                if max_ <= min_:
                    raise Exception(f"OptionsType.Float's data[0] must be smaller than data[1], but got \"{data}\"")
                if steps < 0:
                    raise Exception(f"OptionsType.Float's data[2] must be positive, but got \"{data}\"")
                return OptionsType._get_float_callback(min_, max_, steps)
            raise Exception(f"Expected Tuple of length=3 as OptionsType.Float's data but got \"{data}\".")
        raise Exception(f"Callbacks for OptionsType \"{self.name}\" not yet implemented!")

    @staticmethod
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

    @staticmethod
    def _get_float_callback(min_: float, max_: float, steps: int) -> Tuple[Callable[[int], str], Callable[[str], float]]:
        assert min_ < max_
        assert steps > 0
        range_ = max_ - min_
        step_size = range_ / steps

        def get(index: int) -> str:
            val = round(min_ + step_size * index, ndigits=3)
            return str(val)

        return get, float


class Options(Enum):
    energy_mode = ("Energy Mode", OptionsType.Bool, None, 2, 0,
                   "In energy mode every change to your circuit costs energy. You loose if your Robot is out of "
                   "energy.")

    auto_save = ("Auto Save", OptionsType.Bool, None, 2, 1,
                 "Whether to automatically save the game on exit or not.")
    auto_reset_circuit = ("Auto Reset Circuit", OptionsType.Bool, None, 2, 1,
                          "Automatically reset your Circuit to a clean state at the beginning of a Puzzle, Riddle, "
                          "etc.")
    log_keys = ("Log Keys", OptionsType.Bool, None, 2, 1,
                "Stores all keys you pressed in a .qrkl-file so one can replay them (e.g. for analysing a bug)")

    gameplay_key_pause = ("Gameplay Key Pause", OptionsType.Float, (0.1, 1.0, 9), 9, 0,
                          "How long to wait before we process the next input during gameplay.")
    simulation_key_pause = ("Simulation Key Pause", OptionsType.Float, (0.05, 1.0, 19), 19, 3,
                            "How long to wait before we process the next input during simulation.")

    show_ket_notation = ("Show Ket-Notation", OptionsType.Bool, None, 2, 1,
                         "Whether to display ket-notation for state vectors and circuit matrix or not.")
    allow_implicit_removal = ("Allow implicit Removal", OptionsType.Bool, None, 2, 0,
                              "Allows you to place a gate on an occupied spot, removing the occupying gate in the "
                              "process.")
    allow_multi_move = ("Allow multi move", OptionsType.Bool, None, 2, 0,
                        "Allows you to move multiple tiles at once by pressing a number followed by a direction.")
    auto_skip_text_animation = ("Auto skip text animation", OptionsType.Bool, None, 2, 0,
                                "During some special scene transitions there will be some animated text describing "
                                "what happened in-between story sections. Skipping this means that the whole text "
                                "will be shown at once.")
    enable_puzzle_history = ("Enable puzzle history", OptionsType.Bool, None, 2, 1,
                             "Whether you can navigate through your circuit's history or not while solving a puzzle.")
    auto_reset_history = ("Auto reset history", OptionsType.Bool, None, 2, 1,
                          "Whether the puzzle history should automatically jump to the present (= last changes) when "
                          "you navigate through menus.\nNote: Confirming to edit the circuit always resets history.")

    def __init__(self, name: str, otype: OptionsType, data: Any, num_of_values: int, default_index: int,
                 description: str):
        self.__name = name
        self.__otype = otype
        self.__data = data
        self.__get_value, self.__convert_value = otype.get_callbacks(data)
        self.__num_of_values = num_of_values
        self.__default_index = default_index
        self.__description = description

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> OptionsType:
        return self.__otype

    @property
    def data(self) -> Any:
        return self.__data

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


class OptionsManager:
    __SEPARATOR = "="
    __OPTIONS: Dict[Options, int] = {}

    @staticmethod
    def validate() -> bool:
        # todo: check conversion of value of random index for options?
        try:
            for option in Options:
                option.get_value(0)
            return True
        except:
            return False

    @staticmethod
    def init():
        for val in Options:
            OptionsManager.__OPTIONS[val] = val.default_index

    @staticmethod
    def get_options_next_callback(option: Options) -> Callable[[], str]:
        def next_() -> str:
            # first increment the current index
            next_index = OptionsManager.__OPTIONS[option] + 1
            if next_index >= option.num_of_values:
                next_index = 0
            OptionsManager.__OPTIONS[option] = next_index
            # then return the corresponding new value
            return option.get_value(next_index)
        return next_

    @staticmethod
    def get_option_value(option: Options, convert: Optional[bool] = None, ignore_test_config: Optional[bool] = None) \
            -> Any:
        if convert is None: convert = True
        if ignore_test_config is None: ignore_test_config = False

        cur_index = OptionsManager.__OPTIONS[option]
        if convert:
            if option is Options.simulation_key_pause and TestConfig.is_active() and not ignore_test_config:
                return TestConfig.key_pause()
            return option.convert(cur_index)
        else:
            return option.get_value(cur_index)

    @staticmethod
    def set_option_value(option: Options, value: Any) -> bool:
        try:
            index = OptionsManager._get_closest_index(option, value)
            OptionsManager.__OPTIONS[option] = index
            return True
        except:
            return False

    @staticmethod
    def to_string() -> str:
        lines = [f"{option.name}{OptionsManager.__SEPARATOR}{option.convert(OptionsManager.__OPTIONS[option])}"
                 for option in OptionsManager.__OPTIONS]
        return "\n".join(lines)

    @staticmethod
    def _get_closest_index(option: Options, value: Any) -> int:
        if option.type is OptionsType.Bool:
            if isinstance(value, str):
                return 1 if value.lower().strip() in ["true", "yes", "1"] else 0
            else:
                return 1 if value == 1 else 0

        elif option.type is OptionsType.Float:
            if isinstance(value, str):
                value = float(value.strip())
            if isinstance(value, float):
                min_, max_, steps = option.data
                if value <= min_: return 0
                if value >= max_: return steps  # steps is the maximum index
                # remove the offset of min_ and then check how often step_diff is in the remaining value
                step_diff = (max_ - min_) / steps
                return int(round((value - min_) / step_diff))
            else:
                # invalid type for value, so we return the default index
                return option.default_index

        raise NotImplementedError(f"OptionsType {option.type} not implemented!")

    @staticmethod
    def from_text(log_text: str) -> bool:
        def normalize(text: str) -> str:
            return text.lower().strip(" ")

        for line in log_text.splitlines():
            if len(line.strip(" ")) == 0:
                continue
            try:
                name, value = line.split(OptionsManager.__SEPARATOR)
                name = normalize(name)
                for option in Options:
                    if normalize(option.name) == name:  # compare the normalized names
                        index = OptionsManager._get_closest_index(option, value)
                        OptionsManager.__OPTIONS[option] = index
                        break
            except IndexError:
                return False
            except KeyError:
                return False
        return True
