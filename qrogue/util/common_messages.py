from enum import Enum
from typing import Callable

from qrogue.util import Config, ColorConfig as CC, Logger

_show = None
_ask = None


def set_show_callback(show: Callable[[str, str], None]):
    _show = show


def set_ask_callback(ask: Callable[[str, Callable[[bool], None]], None]):
    _ask = ask


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


class CommonPopups(Enum):
    LockedDoor = ("Door is locked!", _locked_door())
    EventDoor = (Config.scientist_name(), "Hmm, I think we should complete the current task first.")
    WrongDirectionDoor = (Config.scientist_name(), "We sadly cannot access the door from this direction.")
    EntangledDoor = ("Door is entangled!", _entangled_door())
    TutorialBlocked = ("Halt!", _tutorial_blocked())
    NotEnoughMoney = ("$$$", _not_enough_money())
    NoCircuitSpace = ("Nope", _no_space())

    def __init__(self, title: str, text: str):
        self.__title = title
        self.__text = text

    def show(self):
        if _show:
            _show(self.__title, self.__text)
        else:
            Logger.instance().error("CommonMessages' show is None!")


class CommonQuestions(Enum):
    GoingBack = "We are not done yet. \nDo you really want to go back to the spaceship?"
    ProceedToNextMap = "Looks like we cleared this map. Shall we proceed directly to the next one?"

    def __init__(self, text: str):
        self.__text = text

    def ask(self, callback: Callable[[bool], None]):
        #Popup.message(Config.scientist_name(), self.__text)
        #ConfirmationPopup.ask(self.__text, callback)
        if _ask:
            _ask(self.__text, callback)
        else:
            Logger.instance().error("CommonQuestions' ask is None!")
