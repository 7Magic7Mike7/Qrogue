from abc import ABC, abstractmethod
from typing import Tuple, Optional

from qrogue.game.logic.actors import StateVector
from qrogue.game.logic.collectibles import Collectible
from qrogue.util import CheatConfig


class Target(ABC):
    """
    Base class for fight-/puzzle-targets.
    """

    def __init__(self, target: StateVector, reward: Collectible):
        """
        Creates a Target with a given target state vector and a reward.
        :param target: the StateVector to reach
        :param reward: the Collectible to get as a reward
        """
        self.__target: StateVector = target
        self.__reward: Collectible = reward
        self.__is_active: bool = True

    @property
    def state_vector(self) -> StateVector:
        """

        :return: this Target's StateVector
        """
        return self.__target

    @property
    def is_active(self) -> bool:
        """
        By default Targets are active. They turn inactive as soon as their StateVector is reached.

        :return: whether this Target is still active or not
        """
        return self.__is_active

    @property
    def flee_energy(self) -> int:
        """

        :return: how much energy it costs to flee from this Target
        """
        return 1

    def is_reached(self, state_vector: StateVector) -> Tuple[bool, Optional[Collectible]]:
        """
        Checks if the given StateVector is equal to the Target's StateVector. If so, this Target is set inactive and
        will provide its reward.

        :param state_vector: the StateVector to check for equality
        :return: True and a Collectible if the Target is reached, False and None otherwise
        """
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
