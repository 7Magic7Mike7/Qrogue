import enum
from typing import Callable, Tuple, List, Set, Optional

from qrogue.util.util_functions import open_folder
from .options import OptionsManager, Options
from .path_config import PathConfig
from .test_config import TestConfig
from .visual_config import PopupConfig, PyCuiColors


class MapConfig:
    @staticmethod
    def num_of_lessons() -> int:
        return 5  # Lesson 0 to 4

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
    def unlock_prefix() -> str:
        return "unlock_"

    @staticmethod
    def next_map_string() -> str:
        return "next"

    @staticmethod
    def back_map_string() -> str:
        return "back"

    @staticmethod
    def level_map_prefix() -> str:
        return "l"

    @staticmethod
    def expedition_map_prefix() -> str:
        return "expedition"

    @staticmethod
    def diff_code_separator() -> str:
        return "d"

    @staticmethod
    def puzzle_seed_separator() -> str:
        return "p"

    @staticmethod
    def tutorial_lesson_prefix() -> str:
        return "l0v"

    @staticmethod
    def first_uncleared() -> str:
        return "firstUncleared"

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

    @staticmethod
    def level_list() -> List[str]:
        levels = []
        for knowledge_level in range(2):
            for i in range(MapConfig.num_of_lessons()):
                levels.append(f"l0k{knowledge_level}v{i}")
        # levels += ["l0training", "l0exam"]
        return levels


class CheatConfig:
    # __ALL and __NONE do not toggle! They simply set or reset all "real" cheats. All other/"real" cheats are toggles.
    __ALL = "aLL"
    __GOD_MODE = "Qod-Mode"     # puzzle checks always succeed, regardless of your circuit or additional constraints
    __INF_EDITS = "Supertry"    # riddles (e.g., boss puzzles) allow for infinite many edits
    __SCARED_RABBIT = "Rabbit_Tunnel"   # all non-0 enemies allways flee
    __INF_RESOURCES = "Rich"    # you're always at max resources (keys, energy)
    __MAP_REVEAL = "Illuminati"     # all areas are visible
    __OBSTACLE_IGNORE = "Obstacle-Iqnor"    # obstacles are walkable
    __MESSAGE_IGNORE = "Lequsi"  # can only see messages via history (including options and help menus)
    __NONE = "n0n3"
    __CHEATS = {
        __GOD_MODE: False,
        __INF_EDITS: False,
        __SCARED_RABBIT: False,
        __INF_RESOURCES: False,
        __MAP_REVEAL: False,
        __OBSTACLE_IGNORE: False,
        __MESSAGE_IGNORE: False,
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
    def has_infinite_edits() -> bool:
        return CheatConfig.__CHEATS[CheatConfig.__INF_EDITS]

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
    def ignore_dialogue(importance: PopupConfig.Importance) -> bool:
        if importance <= PopupConfig.Importance.Dialogue:
            return CheatConfig.__CHEATS[CheatConfig.__MESSAGE_IGNORE]
        else:
            return False  # messages more important than dialogue are not ignored

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
        CheatConfig.__popup("List of Cheats", text, PopupConfig.default_position(), PopupConfig.default_color())

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
        elif code.lower().strip() == "userdata":
            try:
                open_folder(PathConfig.user_data_path())
            except Exception as ex:
                CheatConfig.__popup("Error", f"Failed to open folder at {PathConfig.user_data_path()}: {ex}",
                                    PopupConfig.default_position(), PopupConfig.default_color())

        if ret:
            CheatConfig.__popup("Cheats", f"Successfully used the Cheat \"{code}\"", PopupConfig.default_position(),
                                PopupConfig.default_color())
            CheatConfig.__cheated = True
        else:
            CheatConfig.__popup("Cheats", "This is not a valid Cheat!", PopupConfig.default_position(),
                                PopupConfig.default_color())
        return ret

    @staticmethod
    def use_cheat(code: str) -> bool:
        assert TestConfig.is_active(), "You are not allowed to cheat outside of testing!"
        return CheatConfig.__use_cheat(code)


class GameplayConfig:
    class _KnowledgeMode(enum.Enum):
        Newbie = 0
        Experienced = 1

    __KNOWLEDGE_MODE: _KnowledgeMode = _KnowledgeMode.Newbie

    @staticmethod
    def set_newbie_mode():
        GameplayConfig.__KNOWLEDGE_MODE = GameplayConfig._KnowledgeMode.Newbie

    @staticmethod
    def set_experienced_mode():
        GameplayConfig.__KNOWLEDGE_MODE = GameplayConfig._KnowledgeMode.Experienced

    @staticmethod
    def set_knowledge_mode(km: int) -> bool:
        if km == 0:
            GameplayConfig.set_newbie_mode()
            return True
        elif km == 1:
            GameplayConfig.set_experienced_mode()
            return True
        return False

    @staticmethod
    def get_knowledge_mode() -> int:
        return GameplayConfig.__KNOWLEDGE_MODE.value

    @staticmethod
    def is_newbie_mode():
        return GameplayConfig.__KNOWLEDGE_MODE == GameplayConfig._KnowledgeMode.Newbie

    @staticmethod
    def is_experienced_mode():
        return GameplayConfig.__KNOWLEDGE_MODE == GameplayConfig._KnowledgeMode.Experienced

    @staticmethod
    def get_option_value(option: Options, convert: Optional[bool] = None, ignore_test_config: Optional[bool] = None):
        return OptionsManager.get_option_value(option, convert, ignore_test_config)


class PuzzleConfig:
    BOSS_FLEE_ENERGY = 10
    BOSS_FAIL_DAMAGE = 5

    @staticmethod
    def calculate_appearance_chance(eid: int) -> float:
        return 0.1 * (10 - eid)  # the lower the id the higher the chance of a puzzle to appear

    @staticmethod
    def calculate_flee_chance(eid: int) -> float:
        return PuzzleConfig.calculate_appearance_chance(eid)

    @staticmethod
    def calculate_flee_energy(eid: int) -> int:
        return max(1, eid * 2)


class ScoreConfig:
    # sometimes we cannot provide an expected number of gates (so value = 0) so we need a default to work with
    __DEFAULT_EXPECTED_GATES: int = 5
    _BONUS_FACTOR: float = 2
    _PENALTY_FACTOR: float = 0.7
    _CHECKS_BONUS_MULT: float = 0.2
    _CHECKS_PENALTY_MULT: float = 1.2
    _USED_WEIGHT: float = 0.6
    _CHECKS_WEIGHT: float = 1 - _USED_WEIGHT
    # base score one gets for solving a puzzle etc.
    _BASE_SCORE: int = 100
    _PUZZLE_MULT: float = 1
    _RIDDLE_MULT: float = 1.5
    _CHALLENGE_MULT: float = 1.5
    # bonus score one can get for solving a puzzle etc. in a low amount of steps
    __PUZZLE_BONUS: int = int(_BASE_SCORE * _PUZZLE_MULT)
    __RIDDLE_BONUS: int = int(_BASE_SCORE * _RIDDLE_MULT)
    __CHALLENGE_BONUS: int = int(_BASE_SCORE * _CHALLENGE_MULT * 1.5)

    @staticmethod
    def _f_bonus(ratio: float, factor: float) -> float:
        # ratio should be < 1
        # gives a higher value the smaller ratio is
        return 1 + (1 + factor) * 2 ** (-ratio) - (1 + factor) * 0.5  # 0.5=2**-1, so to normalize it to 1 for ratio==1

    @staticmethod
    def _f_penalty(ratio: float, factor: float) -> float:
        # ratio should be < 1
        # gives a smaller value the smaller ratio is
        return (1 + factor) ** ratio - factor

    @staticmethod
    def _get_ratio(checks: int, used_gates: int, expected_gates: int) -> float:
        """
        Returns a 0 <= value < 2.5 that is higher the better checks and used_gates performs compared to expected_gates.
        This means the lower checks and used_gates are than expected_gates the higher the returned value. Let us
        distinguish three main cases:
            - checks == used_gates == expected_gates: The returned ratio is 1.0 since the puzzle was solved as expected.
            - used_gates < expected_gates: A better solution was found, so a ratio >1.0 is returned. The penalty for needing many checks is kept low.
            - used_gates > expected_gates: A worse solution was found, so a ratio <1.0 is returned. The penalty for needing many checks is increased.
        Keep in mind that checks can never be smaller than used_gates. Therefore, if no combined gates are used
        expected_gates is also the number of expected checks.

        :param checks: how often it was checked if the target was reached
        :param used_gates: how many gates were used to reach the target
        :param expected_gates: how many gates were expected to be needed to reach the target

        :return: a ratio determining how good a puzzle was solved
        """
        assert not (used_gates is None and expected_gates is not None), f"used_gates is None but expected_gates is " \
                                                                        f"{expected_gates}!"
        if used_gates is None or used_gates <= 0:
            used_gates = 1
        if expected_gates is None or expected_gates <= 0:
            # just skip possible bonus since this should only happen for unimportant puzzles
            # and this way we still get a nice curve only depending on checks
            expected_gates = used_gates
        bonus_factor = ScoreConfig._BONUS_FACTOR
        penalty_factor = ScoreConfig._PENALTY_FACTOR

        # expected_gates is also the expected number of checks since you cannot have less checks than gates
        # todo: above is False if we implement combining gates! But good combinations would be rewarded, so it should
        #  be fine
        if used_gates < expected_gates:
            used_exp_val = ScoreConfig._f_bonus(used_gates / expected_gates, bonus_factor)
            # shrink penalty if we used fewer gates
            penalty_factor *= ScoreConfig._CHECKS_BONUS_MULT
        elif used_gates > expected_gates:
            used_exp_val = ScoreConfig._f_penalty(expected_gates / used_gates, penalty_factor)
            # increase penalty if we used more gates (> 1 could lead to negative numbers though)
            penalty_factor = penalty_factor * ScoreConfig._CHECKS_PENALTY_MULT
        else:
            used_exp_val = 1

        if checks < expected_gates:
            checks_exp_val = ScoreConfig._f_bonus(checks / expected_gates, bonus_factor)
        elif checks > expected_gates:
            checks_exp_val = ScoreConfig._f_penalty(expected_gates / checks, penalty_factor)
        else:
            checks_exp_val = 1

        # in our value range it's not possible to get negative values, but theoretically it is
        return max(used_exp_val * ScoreConfig._USED_WEIGHT + checks_exp_val * ScoreConfig._CHECKS_WEIGHT, 0)

    @staticmethod
    def get_puzzle_score(checks: int, used_gates: int, expected_gates: int) -> int:
        """
        Returns a base score plus bonus score depending on how well the puzzle was solved.

        :param checks: how many steps where takes to reach the target
        :param used_gates: how many gates where used in the final circuit
        :param expected_gates: how many gates where used to create the target StateVector

        :return: a score that is bigger the lower checks and used_gates are compared to expected_gates
        """
        ratio = ScoreConfig._get_ratio(checks, used_gates, expected_gates)
        return ScoreConfig._BASE_SCORE + int(ScoreConfig.__PUZZLE_BONUS * ratio)

    @staticmethod
    def compute_time_bonus(score: int, duration: int) -> int:
        return int(score * (1.5 - 0.015 * duration ** 0.74))


class QuantumSimulationConfig:
    DECIMALS = 3
    COMPLEX_DECIMALS = 2  # complex numbers need more space and therefore might show fewer decimals
    TOLERANCE = 0.1
    MAX_SPACE_PER_NUMBER = 1 + 1 + 1 + DECIMALS  # sign + "0" + "." + DECIMALS
    MAX_SPACE_PER_COMPLEX_NUMBER = 1 + 1 + COMPLEX_DECIMALS + 1 + 1 + COMPLEX_DECIMALS + 1  # sign, . & j and decimals
    MAX_PERCENTAGE_SPACE = 3  # the maximum (100%) has three digits


class InstructionConfig:
    MAX_ABBREVIATION_LEN = 3
    COMB_GATE_NAME_MIN_CHARACTERS = 1
    COMB_GATE_NAME_MAX_CHARACTERS = 7
    COMB_GATE_MIN_GATE_NUM = 1
    COMB_GATE_MAX_GATE_NUM = 10


class GateType(enum.Enum):
    # unique by their short name
    IGate = "I", "Identity", set(), \
        "An I Gate or Identity Gate doesn't alter the Qubit in any way. It can be used as a placeholder."
    XGate = "X", "Pauli X", {"Pauli-X", "NOT"}, \
        "In the classical world an X Gate corresponds to an inverter or Not Gate.\n" \
        "It swaps the amplitudes of |0> and |1>.\n" \
        "In the quantum world this corresponds to a rotation of 180° along the x-axis, hence the name X Gate."
    SXGate = "SX", "Square Root X", {"Sqrt X"}, \
        "An SX Gate is the square root of an X Gate. This means multiplying two SX Gates (i.e., placing them in " \
        "series) results in an X Gate. Therefore, it corresponds to a rotation of 90° along the x-axis."
    YGate = "Y", "Pauli Y", {"Pauli-Y"}, \
        "A Y Gate rotates the Qubit along the y-axis by 180°."
    ZGate = "Z", "Pauli Z", {"Pauli-Z"}, \
        "A Z Gate rotates the Qubit along the z-axis by 180°."
    HGate = "H", "Hadamard", set(), \
        "The Hadamard Gate is often used to bring Qubits into Superposition."

    SGate = "S", "Phase", {"P", "Phase Shift S"}, \
        "The S Gate can change the phase of a qubit by multiplying its |1> with j (note that this does not alter " \
        "the probability of measuring |0> or |1>!). It is equivalent to a rotation along the z-axis by 90°."
    RYGate = "RY", "Rotational Y", {"Rot Y"}, \
        "The RY Gate conducts a rotation along the y-axis by a certain angle. In our case the angle is 90°."
    RZGate = "RZ", "Rotational Z", {"Rot Z", "Phase Shift Z", "Phase Flip"}, \
        "The RZ Gate conducts a rotation along the z-axis by a certain angle. In our case the angle is 90°."

    SwapGate = "SW", "Swap", set(), \
        "As the name suggests, Swap Gates swap the amplitude between two Qubits."
    CXGate = "CX", "Controlled X", {"CNOT", "Controlled NOT"}, \
        "Applies an X Gate onto its second Qubit (=target) if its first Qubit (=control) is 1."
    CYGate = "CY", "Controlled Y", set(), \
        "Applies a Y Gate onto its second Qubit (=target) if its first Qubit (=control) is 1."
    CZGate = "CZ", "Controlled Z", set(), \
        "Applies a Z Gate onto its second Qubit (=target) if its first Qubit (=control) is 1."
    CHGate = "CH", "Controlled H", {"Controlled Hadamard"}, \
        "Apples an H Gate onto its second Qubit (=target) if its first Qubit (=control) is 1."

    Combined = "Q", "Qombined", set(), \
        "This gate is a combination of multiple gates fused into one."

    Debug = "de", "Debug", set(), "Only use for debugging!"  # used to test spacing

    def __init__(self, short_name: str, full_name: str, other_names: Set[str], description: str):
        self.__short_name = short_name
        self.__full_name = full_name
        self.__other_names = other_names
        self.__description = description

    @property
    def short_name(self) -> str:
        return self.__short_name

    @property
    def full_name(self) -> str:
        return self.__full_name + " Gate"

    @property
    def has_other_names(self) -> bool:
        return len(self.__other_names) > 0

    @property
    def description(self) -> str:
        return self.__description

    def is_in_names(self, name: str) -> bool:
        names = {self.__short_name, self.__full_name}
        for other_name in self.__other_names: names.add(other_name)

        if name in names:
            return True
        name = name.lower()
        for n in names:
            if name == n.lower():
                return True
        return False

    def get_other_names(self, separator: str = ", ") -> str:
        return separator.join(self.__other_names)


class ExpeditionConfig:
    DEFAULT_QUEUE_SIZE = 0
    DEFAULT_DIFFICULTY = 2
