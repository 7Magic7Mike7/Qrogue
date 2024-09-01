import enum
from typing import Dict, List, Optional

from .util_functions import enum_string


class DifficultyType(enum.Enum):
    # how much of the circuit space should be used up, values in [0, 1]
    CircuitExuberance = ("Circuit Exuberance", 1.15)
    # how many of the available qubits should be rotated, values in [0, 1]
    QubitExuberance = ("Qubit Exuberance", 1.15)
    # how many changed qubits should receive a second rotation, values in [0, 1]
    RotationExuberance = ("Rotation Exuberance", 0.7)
    # how many angles are available to rotations, values are any integers (negatives imply unrestricted real angles)
    RandomizationDegree = ("Randomization Degree", 0.9)
    # how many additional edits are given based on used gates, values >= 0
    BonusEditRatio = ("Bonus Edit Ratio", 1.1)

    # how many gates are at least needed to pick from during stv generation
    MinAvailableGates = "Minimum Available Gates", 1
    # how many unique gates are at least needed to pick form during stv generation
    MinGateVariety = "Minimum Gate Variety", 1
    # minimum difficulty sum among all available gates for stv generation
    MinGateDifficulty = "Minimum Gate Difficulty Sum", 1

    def __init__(self, name: str, level_ratio: float):
        self.__name = name
        self.__level_ratio = level_ratio  # how much this difficulty type affects the overall difficulty level

    @property
    def name(self) -> str:
        return self.__name

    @property
    def _level_ratio(self) -> float:
        return self.__level_ratio

    def __str__(self) -> str:
        return self.__name


class StvDifficulty:
    """This class is immutable."""

    __DIFF_VALUES: Dict[DifficultyType, List[int]] = {
        # during generation
        DifficultyType.CircuitExuberance:   [0.7, 0.75, 0.8, 0.85, 0.9, 1.0],
        DifficultyType.QubitExuberance:     [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RotationExuberance:  [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RandomizationDegree: [  2,   4,  10,  19,  37,  0],
        DifficultyType.BonusEditRatio:      [4.0, 3.3, 2.5, 1.6, 0.9, 0.3],
        # pre generation (i.e., preparation)
        DifficultyType.MinAvailableGates:   [  1,   3,   4,   5,   6,   8],
        DifficultyType.MinGateVariety:      [  1,   2,   3,   4,   5,   7],
        DifficultyType.MinGateDifficulty:   [  0,   5,  10,  15,  20,  30],
    }

    @staticmethod
    def _get_diff_value(diff_type: DifficultyType, level: int) -> float:
        index = level - StvDifficulty.min_difficulty_level()   # normalize level to index
        return StvDifficulty.__DIFF_VALUES[diff_type][index]

    @staticmethod
    def min_difficulty_level() -> int:
        return 0

    @staticmethod
    def max_difficulty_level() -> int:
        return StvDifficulty.num_of_difficulty_levels() - 1

    @staticmethod
    def num_of_difficulty_levels() -> int:
        return len(StvDifficulty.__DIFF_VALUES[DifficultyType.CircuitExuberance])

    @staticmethod
    def degrees_of_freedom() -> int:
        return len(StvDifficulty.__DIFF_VALUES)

    @staticmethod
    def code_len() -> int:
        return StvDifficulty.degrees_of_freedom() * len(str(StvDifficulty.max_difficulty_level()))

    @staticmethod
    def validate() -> bool:
        test_diff = StvDifficulty.from_difficulty_code("1")
        for diff_type, values in StvDifficulty.__DIFF_VALUES.items():
            if len(values) != StvDifficulty.num_of_difficulty_levels():
                return False
            if test_diff.get_absolute_value(diff_type, 1, 1) is None:
                return False    # a conversion is missing
        return True

    @staticmethod
    def _calc_avg_level(values: Dict[DifficultyType, int]) -> int:
        level_sum = sum([values[diff_type] * diff_type._level_ratio for diff_type in values])
        return int(level_sum / len(values))

    @staticmethod
    def _compute_absolute_value(diff_type: DifficultyType, diff_dict: Dict[DifficultyType, float], num_of_qubits: int,
                                circuit_space: int, fallback_value: Optional[float]) -> int:
        if diff_type in diff_dict:
            rel_val = diff_dict[diff_type]
        else:
            rel_val = fallback_value

        if diff_type is DifficultyType.CircuitExuberance:
            return int(rel_val * circuit_space)
        if diff_type is DifficultyType.QubitExuberance:
            return int(rel_val * num_of_qubits)
        if diff_type is DifficultyType.RotationExuberance:
            return int(rel_val * StvDifficulty._compute_absolute_value(DifficultyType.QubitExuberance, diff_dict,
                                                                       num_of_qubits, circuit_space, fallback_value))
        if diff_type is DifficultyType.RandomizationDegree:
            return int(rel_val)
        if diff_type is DifficultyType.BonusEditRatio:
            return int(rel_val * StvDifficulty._compute_absolute_value(DifficultyType.CircuitExuberance, diff_dict,
                                                                       num_of_qubits, circuit_space, fallback_value))

        # the following DifficultyTypes only have absolute values, so no need for additional computations
        if diff_type in [DifficultyType.MinAvailableGates, DifficultyType.MinGateVariety,
                         DifficultyType.MinGateDifficulty]:
            return int(diff_dict[diff_type])
        raise NotImplementedError(f"No absolute value computation implemented for {enum_string(diff_type)}")

    """
    circuit_exuberance: how full (]0, 1]) the circuit should be, e.g., 0.5 = half of the circuit_space is
        used, while 1.0 implies all of it is used (if possible based on gates actually available to create the
        puzzle)
    qubit_exuberance: how many of the qubits  (]0, 1]) should be rotated randomly, e.g., 0.5 rotates half of
        all qubits, while 1.0 rotates all of them once
    rotation_exuberance: how many rotated qubits ([0, 1]) should be rotated along a second axis
    randomization_degree: how many angles are available to random rotations (2*PI / randomization_degree),
        a value of 0 implies no restrictions (i.e., any real number is allowed)
    bonus_edit_ratio: how many additional edits the puzzle provides relative to the number of used gates,
        e.g., a value of 1.0 means that the player has twice as many edits as gates actually needed to solve the
        puzzle, needs to be >= 0
    """

    @staticmethod
    def from_difficulty_code(code: str, num_of_qubits: int = 0, circuit_space: int = 0) -> "StvDifficulty":
        level_len = len(str(StvDifficulty.max_difficulty_level()))  # how many characters a single level code has
        if len(code) == level_len:
            code = code * StvDifficulty.degrees_of_freedom()   # extend code so every DiffType has the same level

        values: Dict[DifficultyType, int] = {}
        for i, diff_type in enumerate(DifficultyType):
            if i >= len(code):
                cur_level = StvDifficulty._calc_avg_level(values)   # extend by average if code is too short
            else:
                cur_level = int(code[i * level_len:(i+1) * level_len])
            values[diff_type] = cur_level
        return StvDifficulty(values)

    @staticmethod
    def from_difficulty_level(level: int, num_of_qubits: int = 0, circuit_space: int = 0) -> "StvDifficulty":
        assert StvDifficulty.min_difficulty_level() <= level <= StvDifficulty.max_difficulty_level(), "Invalid level: " \
            f"{StvDifficulty.min_difficulty_level()} <= {level} <= {StvDifficulty.max_difficulty_level()} is False!"
        return StvDifficulty.from_difficulty_code(str(level))

    def __init__(self, level_values: Dict[DifficultyType, int]):
        self.__level_values = level_values.copy()
        self.__level = StvDifficulty._calc_avg_level(level_values)

    @property
    def level(self) -> int:
        return self.__level

    def get_level(self, diff_type: DifficultyType) -> int:
        if diff_type in self.__level_values:
            return self.__level_values[diff_type]
        # return the general level if no specific level exists for diff_type
        return self.__level

    def get_relative_value(self, diff_type: DifficultyType) -> float:
        level = self.get_level(diff_type)
        assert StvDifficulty.min_difficulty_level() <= level <= StvDifficulty.max_difficulty_level(), \
            "Invalid difficulty level: " \
            f"{StvDifficulty.min_difficulty_level()} <= {level} <= {StvDifficulty.max_difficulty_level()} is False!"
        return StvDifficulty._get_diff_value(diff_type, level)

    def get_absolute_value(self, diff_type: DifficultyType, num_of_qubits: int, circuit_space: int) -> int:
        diff_dict = {}
        for dt in DifficultyType:
            diff_dict[dt] = self.get_relative_value(dt)
        fallback_value = StvDifficulty._get_diff_value(diff_type, self.level)
        return StvDifficulty._compute_absolute_value(diff_type, diff_dict, num_of_qubits, circuit_space, fallback_value)

    def get_absolute_dict(self, num_of_qubits: int, circuit_space: int) -> Dict[DifficultyType, int]:
        # 1) prepare all relative values
        rel_diff_dict = {}
        for diff_type in DifficultyType: rel_diff_dict[diff_type] = self.get_relative_value(diff_type)
        # 2) prepare the absolute values based on the relative ones
        abs_diff_dict = {}
        for diff_type in DifficultyType:
            fallback_value = StvDifficulty._get_diff_value(diff_type, self.level)
            abs_diff_dict[diff_type] = StvDifficulty._compute_absolute_value(diff_type, rel_diff_dict, num_of_qubits,
                                                                             circuit_space, fallback_value)
        return abs_diff_dict

    def to_code(self) -> str:
        return "".join([str(self.get_level(diff_type)) for diff_type in DifficultyType])

    def __str__(self) -> str:
        return f"StvDifficulty({self.to_code()})"
