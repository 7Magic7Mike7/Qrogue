from typing import Callable

from qrogue.util.config import PyCuiColors
from qrogue.util.config import PopupConfig


class MapConfig:
    @staticmethod
    def num_of_lessons() -> int:
        return 7

    @staticmethod
    def max_width() -> int:
        return 7

    @staticmethod
    def max_height() -> int:
        return 3

    @staticmethod
    def done_event_id() -> str:
        return "done"

    @staticmethod
    def specific_done_event_id(completed_map: str) -> str:
        return f"{completed_map}{MapConfig.done_event_id()}"

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
        return "l1v2"


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
    def init(popup_callback: Callable[[str, str, int], None],
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
        CheatConfig.__popup("List of Cheats", text, PopupConfig.default_color())

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
            CheatConfig.__popup("Cheats", f"Successfully used the Cheat \"{code}\"", PopupConfig.default_color())
            CheatConfig.__cheated = True
        else:
            CheatConfig.__popup("Cheats", "This is not a valid Cheat!", PopupConfig.default_color())
        return ret


class GameplayConfig:
    __KEY_VALUE_SEPARATOR = "="

    __AUTO_SAVE = "Auto save on exit"
    __AUTO_RESET_CIRCUIT = "Auto reset Circuit"
    __AUTO_SWAP_GATES = "Auto swap Gates"
    __LOG_KEYS = "Log Keys"
    __SIMULATION_KEY_PAUSE = "Simulation key pause"
    __GAMEPLAY_KEY_PAUSE = "Gameplay key pause"
    __CONFIG = {
        __AUTO_SAVE: ("True", "Automatically saves the game when you exit it."),
        __AUTO_RESET_CIRCUIT: ("True", "Automatically reset your Circuit to a clean state at the beginning of a Fight, "
                                       "Riddle, etc."),
        __AUTO_SWAP_GATES: ("True", "Automatically swaps position of two gates if you try to move one to an occupied "
                                    "slot."),
        __LOG_KEYS: ("True", "Stores all keys you pressed in a .qrkl-file so one can replay them (e.g. for analysing a "
                             "bug)"),
        __SIMULATION_KEY_PAUSE: ("0.2", "How long to wait before we process the next input during simulation."),
        __GAMEPLAY_KEY_PAUSE: ("0.1", "How long to wait before we process the next input during gameplay."),
    }

    @staticmethod
    def to_file_text() -> str:
        text = ""
        for conf in GameplayConfig.__CONFIG:
            text += f"{conf}{GameplayConfig.__KEY_VALUE_SEPARATOR}{GameplayConfig.__CONFIG[conf][0]}"
            text += "\n"
        return text

    @staticmethod
    def from_log_text(log_text: str) -> bool:
        for line in log_text.splitlines():
            split = line.split(GameplayConfig.__KEY_VALUE_SEPARATOR)
            try:
                GameplayConfig.__CONFIG[split[0]] = [split[1]]
            except IndexError:
                return False
            except KeyError:
                return False
        return True

    @staticmethod
    def auto_save() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_SAVE][0] == "True"

    @staticmethod
    def auto_reset_circuit() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_RESET_CIRCUIT][0] == "True"

    @staticmethod
    def log_keys() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__LOG_KEYS][0] == "True"

    @staticmethod
    def simulation_key_pause() -> float:
        try:
            return float(GameplayConfig.__CONFIG[GameplayConfig.__SIMULATION_KEY_PAUSE][0])
        except :
            return 0.2

    @staticmethod
    def gameplay_key_pause() -> float:
        try:
            return float(GameplayConfig.__CONFIG[GameplayConfig.__GAMEPLAY_KEY_PAUSE][0])
        except:
            return 0.4

    @staticmethod
    def auto_swap_gates() -> bool:
        return GameplayConfig.__CONFIG[GameplayConfig.__AUTO_SWAP_GATES][0] == "True"


class PuzzleConfig:
    @staticmethod
    def calculate_appearance_chance(eid: int) -> float:
        return 0.1 * (10 - eid)   # the lower the id the higher the chance of a puzzle to appear

    @staticmethod
    def calculate_flee_chance(eid: int) -> float:
        return PuzzleConfig.calculate_appearance_chance(eid)


class QuantumSimulationConfig:
    DECIMALS = 3
    MAX_SPACE_PER_NUMBER = 1 + 1 + 1 + DECIMALS  # sign + "0" + "." + DECIMALS
    TOLERANCE = 0.1


class ShopConfig:
    @staticmethod
    def base_unit() -> int:
        return 1


class InstructionConfig:
    MAX_ABBREVIATION_LEN = 3
