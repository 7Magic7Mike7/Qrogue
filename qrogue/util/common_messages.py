from enum import Enum
from typing import Callable, Optional, List, Tuple

from qrogue.util import Config, ColorConfig as CC, Logger


class _CallbackHandler:
    __show: Callable[[str], None] = None
    __show_info: Callable[[str, str], None] = None
    __ask: Callable[[str, str, Callable[[int], None], Optional[List[str]]], None] = None

    @staticmethod
    def show(text: str):
        if _CallbackHandler.__show:
            _CallbackHandler.__show(text)
        else:
            Logger.instance().error("CommonMessages' show is None!", from_pycui=False)

    @staticmethod
    def set_show_callback(show: Callable[[str], None]):
        _CallbackHandler.__show = show

    @staticmethod
    def set_show_info_callback(show_info_callback: Callable[[str, str], None]):
        _CallbackHandler.__show_info = show_info_callback

    @staticmethod
    def show_info(title: str, text: str):
        if _CallbackHandler.__show_info:
            _CallbackHandler.__show_info(title, text)
        else:
            Logger.instance().error("CommonMessages' show_info is None!", from_pycui=False)

    @staticmethod
    def ask(title: str, text: str, callback: Callable[[int], None], answers: Optional[List[str]]):
        if _CallbackHandler.__ask:
            _CallbackHandler.__ask(title, text, callback, answers)
        else:
            Logger.instance().error("CommonMessages' ask is None!", from_pycui=False)

    @staticmethod
    def set_ask_callback(ask: Callable[[str, str, Callable[[int], None]], None]):
        _CallbackHandler.__ask = ask


def set_show_callback(show: Callable[[str], None]):
    _CallbackHandler.set_show_callback(show)


def set_show_info_callback(show_info: Callable[[str, str], None]):
    _CallbackHandler.set_show_info_callback(show_info)


def set_ask_callback(ask: Callable[[str, str, Callable[[int], None], Optional[List[str]]], None]):
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
    LockedDoor = _locked_door()
    EventDoor = "Access denied. Permission requirements not yet fulfilled."
    WrongDirectionDoor = "Access denied. Door cannot be accessed from this side."
    EntangledDoor = _entangled_door()
    TutorialBlocked = _tutorial_blocked()
    NotEnoughMoney = _not_enough_money()
    NoCircuitSpace = _no_space()
    NoGatePlaced = _no_gate_placed()
    NotEnoughEnergyToFlee = _not_enough_energy_to_flee()

    def __init__(self, text: str):
        self.__text = text

    @property
    def text(self) -> str:
        return self.__text

    def show(self):
        _CallbackHandler.show(self.__text)


class CommonInfos(Enum):
    SavingFailed = ("Error!", "Failed to save the game. Please make sure the folder for save data still exists and try "
                              "again.")
    SavingSuccessful = ("Saved", "You successfully saved the game!")
    NoSavingWithCheats = ("Cheating", "You used a cheat and therefore are not allowed to save the game!")
    NoSavingDuringSimulation = ("Simulating", "Saving is not allowed during simulation.")
    NothingToSave = ("Nothing to save", "Your latest data has already been successfully saved.")
    OptionsSaved = ("Saved", "You successfully saved your changes to the options!")
    OptionsNotSaved = ("Error!", "Could not save your changes...")

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
        _CallbackHandler.show_info(self.__title, self.__text)


class CommonQuestions(Enum):
    GoingBack = (Config.scientist_name(), "We are not done yet. \nDo you really want to go back?")
    ProceedToNextMap = (Config.scientist_name(), "Looks like we cleared this map. Shall we proceed directly to the " 
                                                 "next one?", ["Proceed", "Stay", "Back to world"])
    UseTeleporter = (Config.system_name(), "Do you want to use this Teleporter?")
    SkipStoryTutorial = (Config.system_name(), "Warning: It is recommended to first finish the tutorial parts of the "
                                               "story. Only continue if you're already familiar with Quantum Computing "
                                               "and know what you're doing!")
    OpenUserDataFolder = (Config.system_name(), "Do you want to open the folder containing your user data with your "
                                                "system's explorer?")
    BackToMenu = (Config.system_name(), "Do you want to return to the main menu?")

    @staticmethod
    def proceed_summary(level_name: str, score: int, duration: int, total_score: int, callback: Callable[[int], None],
                        prev_values: Optional[Tuple[int, int]] = None):
        text = f"{level_name}\n" \
                f"Score:       {score}\n" \
                f"Duration:    {duration}s\n" \
                f"Total Score: {total_score}"
        if prev_values is not None:
            text += f"\n\n" \
                    f"Highscore:   {prev_values[0]}\n" \
                    f"Duration:    {prev_values[1]}"
        _CallbackHandler.ask(Config.system_name(), text, callback, ["Proceed", "Stay", "Back to Main Menu"])    # todo: does stay work?

    def __init__(self, title: str, text: str, answers: Optional[List[str]] = None):
        self.__title = title
        self.__text = text
        self.__answers = answers

    def ask(self, callback: Callable[[int], None]):
        _CallbackHandler.ask(self.__title, self.__text, callback, self.__answers)
