from abc import ABC, abstractmethod
from typing import Tuple, Optional

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import Logger


class Target(ABC):
    """
    Base class for fight-/puzzle-targets.
    """

    def __init__(self, target: StateVector, reward: Collectible, input_: Optional[StateVector] = None,
                 allow_target_input_equality: bool = False):
        """
        Creates a Target with a given target state vector and a reward.
        :param target: the StateVector to reach
        :param reward: the Collectible to get as a reward
        :param input_: the StateVector to start with (all |0> by default)
        :param allow_target_input_equality: whether target and input are allowed to be equal (would make basic puzzles
        be solved from the beginning, hence default is False)
        """
        self.__target: StateVector = target
        self.__reward: Collectible = reward
        self.__input: StateVector = StateVector.create_zero_state_vector(target.num_of_qubits) if input_ is None \
            else input_
        self.__is_active: bool = True
        # how often the target was checked (i.e., if it was reached) - can be used to determine the rewarded score
        self.__checks: int = 0

        if not allow_target_input_equality and self.__target.is_equal_to(self.__input, ignore_god_mode=True):
            Logger.instance().warn(f"@Target.init(): target is equal to input (={self.__target})!", from_pycui=False)

    @property
    def state_vector(self) -> StateVector:
        """

        :return: this Target's StateVector
        """
        return self.__target

    @property
    def input_stv(self) -> StateVector:
        return self.__input

    @property
    def is_active(self) -> bool:
        """
        By default, Targets are active. They turn inactive as soon as their StateVector is reached.

        :return: whether this Target is still active or not
        """
        return self.__is_active

    @property
    def flee_energy(self) -> int:
        """

        :return: how much energy it costs to flee from this Target
        """
        return 1

    @property
    def checks(self) -> int:
        """
        Counts how often a player checked if the target StateVector was reached. Is used to determine the score gained
        from solving puzzles etc.

        :return: how often is_reached() was called
        """
        return self.__checks

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Optional[Collectible]]:
        """
        Checks if the given StateVector is equal to the Target's StateVector. If so, this Target is set inactive and
        will provide its reward.

        :param state_vector: the StateVector to check for equality
        :return: True and a Collectible if the Target is reached, False and None otherwise
        """
        self.__checks += 1
        if self.__target.is_equal_to(state_vector):
            self._on_reached()
            self.__is_active = False
            temp = self.__reward
            self.__reward = None
            return True, temp
        return False, None

    @abstractmethod
    def _on_reached(self):
        """
        Is called during a successful is_reached(). Gives Subclasses the possibility to react to the internal state
        change.

        :return: None
        """
        pass

    def __str__(self):
        string = "["
        for q in self.__target.to_value():
            string += f"{q} "
        string += "]"
        return string
