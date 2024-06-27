import enum
from typing import Dict, Optional, List

from .logger import Logger


class StvDifficulty:
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
            self.__level_ratio = level_ratio    # how much this difficulty type affects the overall difficulty level

        @property
        def name(self) -> str:
            return self.__name

        @property
        def _level_ratio(self) -> float:
            return self.__level_ratio

        def __str__(self) -> str:
            return self.__name

    __DIFF_VALUES: Dict[DifficultyType, List[int]] = {
        DifficultyType.CircuitExuberance:   [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.QubitExuberance:     [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RotationExuberance:  [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        DifficultyType.RandomizationDegree: [  2,   4,  10,  19,  37,  0],
        DifficultyType.BonusEditRatio:      [2.0, 1.5, 1.0, 0.6, 1.3, 0.0],
    }

    @staticmethod
    def max_difficulty_level() -> int:
        return len(StvDifficulty.__DIFF_VALUES[StvDifficulty.DifficultyType.CircuitExuberance])

    @staticmethod
    def degrees_of_freedom() -> int:
        return len(StvDifficulty.__DIFF_VALUES)

    @staticmethod
    def code_len() -> int:
        return StvDifficulty.degrees_of_freedom() * len(str(StvDifficulty.max_difficulty_level()))

    @staticmethod
    def validate() -> bool:
        for values in StvDifficulty.__DIFF_VALUES.values():
            if len(values) != StvDifficulty.max_difficulty_level():
                return False
        return True

    @staticmethod
    def _calc_avg_level(values: Dict[DifficultyType, int]) -> int:
        level_sum = 0
        for val in StvDifficulty.DifficultyType:
            if val in values:
                level_sum += values[val] * val._level_ratio
        return int(level_sum / len(values))

    @staticmethod
    def from_percentages(num_of_qubits: int, circuit_space: int, circuit_exuberance: float, qubit_exuberance: float,
                         rotation_exuberance: float, randomization_degree: int, bonus_edit_ratio: float,
                         level: Optional[int] = None) -> "StvDifficulty":
        """

        :param num_of_qubits: number of qubits available
        :param circuit_space: maximum number of gates that can be placed in the circuit
        :param circuit_exuberance: how full (]0, 1]) the circuit should be, e.g., 0.5 = half of the circuit_space is
            used, while 1.0 implies all of it is used (if possible based on gates actually available to create the
            puzzle)
        :param qubit_exuberance: how many of the qubits  (]0, 1]) should be rotated randomly, e.g., 0.5 rotates half of
            all qubits, while 1.0 rotates all of them once
        :param rotation_exuberance: how many rotated qubits ([0, 1]) should be rotated along a second axis
        :param randomization_degree: how many angles are available to random rotations (2*PI / randomization_degree),
            a value of 0 implies no restrictions (i.e., any real number is allowed)
        :param bonus_edit_ratio: how many additional edits the puzzle provides relative to the number of used gates,
            e.g., a value of 1.0 means that the player has twice as many edits as gates actually needed to solve the
            puzzle, needs to be >= 0
        :param level: level of the difficulty
        """
        assert 0 < circuit_exuberance <= 1.0, f"Invalid circuit exuberance: 0 < {circuit_exuberance} <= 1 is False!"
        assert 0 < qubit_exuberance <= 1.0, f"Invalid qubit exuberance: 0 < {qubit_exuberance} <= 1 is False!"
        assert 0 <= rotation_exuberance <= 1.0, f"Invalid rotation exuberance: 0 < {rotation_exuberance} <= 1 is False!"
        assert 0 <= bonus_edit_ratio, f"Invalid edit ratio: 0 <= {bonus_edit_ratio} is False!"

        num_of_gates = int(circuit_space * circuit_exuberance)
        num_of_rotated_qubits = int(num_of_qubits * qubit_exuberance)
        rotation_degree = int(num_of_rotated_qubits * rotation_exuberance)
        bonus_edits = int(num_of_gates * bonus_edit_ratio)
        return StvDifficulty(num_of_gates, num_of_rotated_qubits, rotation_degree, randomization_degree, bonus_edits,
                             level)

    @staticmethod
    def from_difficulty_dict(num_of_qubits: int, circuit_space: int, values: Dict[DifficultyType, int]) \
            -> "StvDifficulty":
        avg_level = StvDifficulty._calc_avg_level(values)

        def get_diff_val(diff_type: StvDifficulty.DifficultyType) -> int:
            level = values[diff_type] if diff_type in values else avg_level
            return StvDifficulty.__DIFF_VALUES[diff_type][level]
        circuit_exuberance = get_diff_val(StvDifficulty.DifficultyType.CircuitExuberance)
        qubit_exuberance = get_diff_val(StvDifficulty.DifficultyType.QubitExuberance)
        rotation_exuberance = get_diff_val(StvDifficulty.DifficultyType.RotationExuberance)
        randomization_degree = get_diff_val(StvDifficulty.DifficultyType.RandomizationDegree)
        bonus_edit_ratio = get_diff_val(StvDifficulty.DifficultyType.BonusEditRatio)

        return StvDifficulty.from_percentages(num_of_qubits, circuit_space, circuit_exuberance, qubit_exuberance,
                                              rotation_exuberance, randomization_degree, bonus_edit_ratio, avg_level)

    @staticmethod
    def from_difficulty_code(code: str, num_of_qubits: int, circuit_space: int) -> "StvDifficulty":
        level_len = len(str(StvDifficulty.max_difficulty_level()))  # how many characters a single level code has
        if len(code) == level_len:
            code = code * StvDifficulty.degrees_of_freedom()   # extend code so every DiffType has the same level
        assert len(code) <= StvDifficulty.degrees_of_freedom() * level_len, \
            f"Level code \"{code}\" is too short! At least {StvDifficulty.degrees_of_freedom() * level_len} " \
            f"characters are needed."

        values: Dict[StvDifficulty.DifficultyType, int] = {}
        for i, diff_type in enumerate(StvDifficulty.DifficultyType):
            values[diff_type] = int(code[i * level_len:(i+1) * level_len])
        return StvDifficulty.from_difficulty_dict(num_of_qubits, circuit_space, values)

    @staticmethod
    def from_difficulty_level(level: int, num_of_qubits: int, circuit_space: int) -> "StvDifficulty":
        assert 0 <= level < StvDifficulty.max_difficulty_level(), \
            f"Invalid level: 0 <= {level} < {StvDifficulty.max_difficulty_level()} is False!"
        values: Dict[StvDifficulty.DifficultyType, int] = {}
        for diff_type in StvDifficulty.DifficultyType: values[diff_type] = level
        return StvDifficulty.from_difficulty_dict(num_of_qubits, circuit_space, values)

    def __init__(self, num_of_gates: int, num_of_rotated_qubits: int, rotation_degree: int, randomization_degree: int,
                 bonus_edits: int, __level: Optional[int] = None):
        """
        :param randomization_degree: how many angles are available to random rotations (2*PI / randomization_degree),
            a value of 0 implies no restrictions (i.e., any real number is allowed)
        :param bonus_edits: how many more edits than placed gates (min number of needed edits) the player has
        """
        assert num_of_gates > 0, f"At least one gate needs to be placed: {num_of_gates} > 0 is False!"
        assert num_of_rotated_qubits >= 0, f"No negative value allowed for " \
                                           f"num_of_rotated_qubits={num_of_rotated_qubits}"
        assert rotation_degree >= 0, f"No negative value allowed for rotation_degree={rotation_degree}"
        assert randomization_degree >= 0, f"No negative value allowed for randomization_degree={randomization_degree}"

        if rotation_degree > num_of_rotated_qubits:
            Logger.instance().warn(f"rotation_degree (={rotation_degree}) > num_of_rotated_qubits "
                                   f"(={num_of_rotated_qubits}) - using num_of_rotated_qubits instead")
            rotation_degree = num_of_rotated_qubits     # we cannot have more additional rotations than qubits

        self.__num_of_gates = num_of_gates
        self.__num_of_rotated_qubits = num_of_rotated_qubits
        self.__rotation_degree = rotation_degree
        self.__randomization_degree = randomization_degree
        self.__bonus_edits = bonus_edits
        self.__level = -1 if __level is None else __level

    @property
    def is_leveled(self) -> bool:
        return self.__level >= 0

    @property
    def level(self) -> int:
        return self.__level

    @property
    def num_of_gates(self) -> int:
        """
        :return: how many gates can be used to calculate the target
        """
        return self.__num_of_gates

    @property
    def num_of_rotated_qubits(self) -> int:
        """
        :return: how many qubits should be randomly rotated to determine |In>
        """
        return self.__num_of_rotated_qubits

    @property
    def rotation_degree(self) -> int:
        """
        <= num_of_rotated_qubits
        :return: how many rotated qubits should also be rotated along a second axis
        """
        return self.__rotation_degree

    @property
    def randomization_degree(self) -> int:
        """
        A value of 0 implies no restriction (i.e., any real value is allowed)

        :return: how many degrees of freedom the random rotation angles have
        """
        return self.__randomization_degree

    @property
    def edits(self) -> int:
        return self.__num_of_gates + self.__bonus_edits

    def normalize(self, num_of_qubits: int, circuit_space: int) -> "StvDifficulty":
        num_of_gates = circuit_space if circuit_space < self.__num_of_gates else self.__num_of_gates
        num_of_rotated_qubits = num_of_qubits if num_of_qubits < self.__num_of_rotated_qubits\
            else self.__num_of_rotated_qubits
        return StvDifficulty(num_of_gates, num_of_rotated_qubits, self.__rotation_degree, self.__randomization_degree,
                             self.__bonus_edits)
