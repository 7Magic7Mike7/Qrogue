import enum
from abc import ABC, abstractmethod
from typing import List

from qrogue.game.logic.collectibles import Collectible


class ControllableType(enum.Enum):
    """
    Specifies the different types of Controllable for automatic processing (e.g. for color rules).
    """

    Player = "M"        # todo add name to constructor?
    Luke = "L"
    Test = "T"
    Base = "Q"

    @staticmethod
    def values() -> List["ControllableType"]:
        """

        :return: list of all ControllableTypes
        """
        return [ControllableType.Player, ControllableType.Luke, ControllableType.Test, ControllableType.Base]

    def __init__(self, abbreviation: str):
        """
        Initializes the ControllableType with a (unique) abbreviation.

        :param abbreviation: how the Controllable is displayed
        """
        self.__abbreviation = abbreviation

    @property
    def name(self) -> str:
        return self.__abbreviation


class Controllable(ABC):
    """
    A Controllable is the interface between the game's player and the game.
    """

    def __init__(self, name: str):  # todo use ControllableType instead
        self.__name = name

    @property
    def name(self) -> str:
        """

        :return: name of the Controllable
        """
        return self.__name

    @abstractmethod
    def game_over_check(self) -> bool:
        """
        Checks whether the Controllable is game over or not.

        :return: True if the Controllable is game over, False otherwise
        """
        pass

    @abstractmethod
    def key_count(self) -> int:
        """

        :return: how many keys the Controllable can use
        """
        pass

    @abstractmethod
    def use_key(self) -> bool:
        """
        Tries to use one of the Controllable's keys.

        :return: True if a key was used successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_img(self):
        """
        Provides an image for rendering. Return type depends on the renderer we use.

        :return: an image to render the Controllable
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Provides a description to display some prose information about the Controllable. E.g. can be used to show the
        game's player details about the Controllable.

        :return: a short description of the Controllable
        """
        pass

    @abstractmethod
    def give_collectible(self, collectible: Collectible):
        """
        Gives the provided Collectible to the Controllable (e.g. adding it to its inventory).

        :param collectible: a Collectible to give the Controllable
        :return: None
        """
        pass
