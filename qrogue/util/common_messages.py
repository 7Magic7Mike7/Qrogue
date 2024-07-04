from enum import Enum
from typing import Callable, Optional, List, Tuple

from qrogue.util.config import Config, ColorConfig as CC
from qrogue.util.logger import Logger


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


class CommonPopups(Enum):
    LockedDoor = f"Come back with a {CC.highlight_object('Key')} to open the {CC.highlight_object('Door')}."
    EventDoor = "Access denied. Permission requirements not yet fulfilled."
    WrongDirectionDoor = "Access denied. Door cannot be accessed from this side."
    EntangledDoor = f"The {CC.highlight_object('Door')} {CC.highlight_word('entangled')} with this one was opened. " \
                    f"Therefore you can no longer pass this {CC.highlight_object('Door')}."
    TutorialBlocked = f"You should not go there yet! Finish the {CC.highlight_word('current step')} of the " \
                      f"{CC.highlight_word('Tutorial')} first."
    NotEnoughMoney = "You cannot afford that right now. Come back when you have enough money."
    NoCircuitSpace = f"Your {CC.highlight_object('Circuit')} has {CC.highlight_word('no more space')} left. Remove a " \
                     f"{CC.highlight_object('Gate')} to place another one."
    NoGatePlaced = f"Currently there is {CC.highlight_word('no')} {CC.highlight_object('Gate')} in your " \
                   f"{CC.highlight_object('Circuit')} that you could remove!"
    NotEnoughEnergyToFlee = f"{CC.highlight_word('Denied')}. Fleeing {CC.highlight_word('not possible')} because it " \
                            f"would cost all of the {CC.highlight_object('Robot´s')} remaining " \
                            f"{CC.highlight_object('Energy')}."
    CannotFlee = f"You cannot {CC.highlight_action('flee')} from {CC.highlight_object('Challenges')}!"
    BackpackFull = f"Currently there is {CC.highlight_word('no more space')} in your backpack to hold another " \
                   f"{CC.highlight_object('Collectible')}. Please come back as soon as you have enough space!"

    def __init__(self, text: str):
        self.__text = text

    @property
    def text(self) -> str:
        Config.check_reachability("CommonPopups.text")
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
    OpenUserDataFolder = (Config.system_name(), "Do you want to open the folder containing your user data with your "
                                                "system's explorer?")
    BackToMenu = (Config.system_name(), "Do you want to return to the main menu?")

    @staticmethod
    def proceed_summary(level_name: str, score: int, duration: int, total_score: int, callback: Callable[[int], None],
                        prev_values: Optional[Tuple[int, int]] = None):
        text = f"Congratulations for completing \"{level_name}\"\n" \
               f"Your stats:\n" \
               f"Score:       {score}\n" \
               f"Duration:    {duration}s\n" \
               f"Total Score: {total_score}"
        if prev_values is not None:
            text += f"\n\nStats of best attempt:" \
                    f"Duration:    {prev_values[1]}\n" \
                    f"Total Score: {prev_values[0]}"
        _CallbackHandler.ask(Config.system_name(), text, callback, ["Proceed", "Stay", "Back to Main Menu"])    # todo: does stay work?

    def __init__(self, title: str, text: str, answers: Optional[List[str]] = None):
        self.__title = title
        self.__text = text
        self.__answers = answers

    def ask(self, callback: Callable[[int], None]):
        _CallbackHandler.ask(self.__title, self.__text, callback, self.__answers)
