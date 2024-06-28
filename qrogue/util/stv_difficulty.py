import enum
from typing import Dict, List

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
        DifficultyType.CircuitExuberance:   [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.QubitExuberance:     [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RotationExuberance:  [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RandomizationDegree: [  2,   4,  10,  19,  37,  0],
        DifficultyType.BonusEditRatio:      [2.0, 1.5, 1.0, 0.6, 1.3, 0.0],
    }

    @staticmethod
    def min_difficulty_level() -> int:
        return 0

    @staticmethod
    def max_difficulty_level() -> int:
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
            if len(values) != StvDifficulty.max_difficulty_level():
                return False
            if test_diff.get_absolute_value(diff_type, 1, 1) is None:
                return False    # a conversion is missing
        return True

    @staticmethod
    def _calc_avg_level(values: Dict[DifficultyType, int]) -> int:
        level_sum = 0
        for val in DifficultyType:
            if val in values:
                level_sum += values[val] * val._level_ratio
        return int(level_sum / len(values))

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
        assert len(code) <= StvDifficulty.degrees_of_freedom() * level_len, \
            f"Level code \"{code}\" is too short! At least {StvDifficulty.degrees_of_freedom() * level_len} " \
            f"characters are needed."

        values: Dict[DifficultyType, int] = {}
        for i, diff_type in enumerate(DifficultyType):
            values[diff_type] = int(code[i * level_len:(i+1) * level_len])
        return StvDifficulty(values)

    @staticmethod
    def from_difficulty_level(level: int, num_of_qubits: int = 0, circuit_space: int = 0) -> "StvDifficulty":
        assert 0 <= level < StvDifficulty.max_difficulty_level(), \
            f"Invalid level: 0 <= {level} < {StvDifficulty.max_difficulty_level()} is False!"
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
        assert 0 <= level < StvDifficulty.max_difficulty_level(), \
            f"Invalid difficulty level: 0 <= {level} <= {StvDifficulty.max_difficulty_level()} is False!"
        return StvDifficulty.__DIFF_VALUES[diff_type][level]

    def get_absolute_value(self, diff_type: DifficultyType, num_of_qubits: int, circuit_space: int) -> int:
        rel_val = self.get_relative_value(diff_type)
        if diff_type is DifficultyType.CircuitExuberance:
            return int(rel_val * circuit_space)
        if diff_type is DifficultyType.QubitExuberance:
            return int(rel_val * num_of_qubits)
        if diff_type is DifficultyType.RotationExuberance:
            return int(rel_val * self.get_absolute_value(DifficultyType.QubitExuberance, num_of_qubits, circuit_space))
        if diff_type is DifficultyType.RandomizationDegree:
            return int(rel_val)
        if diff_type is DifficultyType.BonusEditRatio:
            return int(rel_val * self.get_absolute_value(DifficultyType.CircuitExuberance, num_of_qubits,
                                                         circuit_space))
        raise NotImplementedError(f"No absolute value calculation implemented for {enum_string(diff_type)}")

    def get_absolute_dict(self, num_of_qubits: int, circuit_space: int) -> Dict[DifficultyType, int]:
        diff_dict = {}
        for diff_type in DifficultyType:
            diff_dict[diff_type] = self.get_absolute_value(diff_type, num_of_qubits, circuit_space)
        return diff_dict

    def to_code(self) -> str:
        return "".join([str(self.get_level(diff_type)) for diff_type in DifficultyType])

    def __str__(self) -> str:
        return f"StvDifficulty({self.to_code()})"
