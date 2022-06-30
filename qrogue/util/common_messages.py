from enum import Enum
from typing import Callable

from qrogue.util import Config, ColorConfig as CC, Logger


class _CallbackHandler:
    __show: Callable[[str, str], None] = None
    __ask: Callable[[str, str, Callable[[bool], None]], None] = None

    @staticmethod
    def show(title: str, text: str):
        if _CallbackHandler.__show:
            _CallbackHandler.__show(title, text)
        else:
            Logger.instance().error("CommonMessages' show is None!")

    @staticmethod
    def set_show_callback(show: Callable[[str, str], None]):
        _CallbackHandler.__show = show

    @staticmethod
    def ask(title: str, text: str, callback: Callable[[bool], None]):
        if _CallbackHandler.__ask:
            _CallbackHandler.__ask(title, text, callback)
        else:
            Logger.instance().error("CommonMessages' ask is None!")

    @staticmethod
    def set_ask_callback(ask: Callable[[str, str, Callable[[bool], None]], None]):
        _CallbackHandler.__ask = ask


def set_show_callback(show: Callable[[str, str], None]):
    _CallbackHandler.set_show_callback(show)


def set_ask_callback(ask: Callable[[str, str, Callable[[bool], None]], None]):
    _CallbackHandler.set_ask_callback(ask)


def _locked_door() -> str:
    key = CC.highlight_object("Key")
    door = CC.highlight_object("Door")
    return f"Come back with a {key} to open the {door}."


def _one_way_door() -> str:
    one_way = CC.highlight_object("one way")
    door = CC.highlight_object("Door")
    return f"This is a {one_way} {door} that can only be opened from the other side!"


def _entangled_door() -> str:
    door = CC.highlight_object("Door")
    entangled = CC.highlight_word("entangled")
    return f"The {door} {entangled} with this one was opened. Therefore you can no longer pass this {door}."


def _tutorial_blocked() -> str:
    step = CC.highlight_word("current step")
    tutorial = CC.highlight_word("Tutorial")
    return f"You should not go there yet! Finish the {step} of the {tutorial} first."


def _not_enough_money() -> str:
    return "You cannot afford that right now. Come back when you have enough money."


def _no_space() -> str:
    circ = CC.highlight_object("Circuit")
    space = CC.highlight_word("no more space")
    gate = CC.highlight_object("Gate")
    return f"Your {circ} has {space} left. Remove a {gate} to place another one."


def _no_gate_placed() -> str:
    no = CC.highlight_word("no")
    gate = CC.highlight_object("Gate")
    circuit = CC.highlight_object("Circuit")
    return f"Currently there is {no} {gate} in your {circuit} that you could remove!"


def _not_enough_energy_to_flee() -> str:
    denied = CC.highlight_word("Denied")
    not_possible = CC.highlight_word("not possible")
    robots = CC.highlight_object("Robot's")
    energy = CC.highlight_object("Energy")
    return f"{denied}. Fleeing {not_possible} because it would cost all of the {robots} remaining {energy}."


class CommonPopups(Enum):
    SavingFailed = ("Error!", "Failed to save the game. Please make sure the folder for save data still exists and try "
                              "again.")
    SavingSuccessful = ("Saved", "You successfully saved the game!")
    NoSavingWithCheats = ("Cheating", "You used a cheat and therefore are not allowed to save the game!")
    LockedDoor = (Config.system_name(), _locked_door())
    EventDoor = (Config.system_name(), "Access denied. Permission requirements not yet fulfilled.")
    WrongDirectionDoor = (Config.system_name(), "Access denied. Door cannot be accessed from this side.")
    EntangledDoor = (Config.system_name(), _entangled_door())
    TutorialBlocked = ("Halt!", _tutorial_blocked())
    NotEnoughMoney = (Config.system_name(), _not_enough_money())
    NoCircuitSpace = (Config.system_name(), _no_space())
    NoGatePlaced = (Config.system_name(), _no_gate_placed())
    NotEnoughEnergyToFlee = (Config.system_name(), _not_enough_energy_to_flee())

    def __init__(self, title: str, text: str):
        self.__title = title
        self.__text = text

    @property
    def title(self) -> str:
        return self.__title

    @property
    def text(self) -> str:
        return self.__text

    def show(self):
        _CallbackHandler.show(self.__title, self.__text)


class CommonQuestions(Enum):
    GoingBack = (Config.scientist_name(), "We are not done yet. \nDo you really want to go back to the spaceship?")
    ProceedToNextMap = (Config.scientist_name(), "Looks like we cleared this map. Shall we proceed directly to the " 
                                                 "next one?")

    def __init__(self, title: str, text: str):
        self.__title = title
        self.__text = text

    def ask(self, callback: Callable[[bool], None]):
        _CallbackHandler.ask(self.__title, self.__text, callback)
