from typing import Callable

from qrogue.game.logic import Message
from qrogue.util import Config, PopupConfig


class Popup:
    __show_popup = None
    __check_achievement = None
    __popup_queue = []
    __cur_popup = None
    __last_popup = None

    @staticmethod
    def update_popup_functions(show_popup_callback: Callable[[str, str, int], None]) -> None:
        Popup.__show_popup = show_popup_callback

    @staticmethod
    def update_check_achievement_function(check_achievement_callback: Callable[[str], bool]) -> None:
        Popup.__check_achievement = check_achievement_callback

    @staticmethod
    def on_close() -> bool:
        if Popup.__cur_popup and Popup.__cur_popup.is_reopenable:
            Popup.__last_popup = Popup.__cur_popup
        Popup.__cur_popup = None
        if len(Popup.__popup_queue) > 0:
            next_popup = Popup.__popup_queue.pop(0)
            next_popup.show()
            return False        # don't fully close popup
        return True     # popup no longer needed so we can fully close it

    @staticmethod
    def reopen():
        if Popup.__last_popup and Popup.__cur_popup is None:
            Popup.__last_popup.show()

    @staticmethod
    def message(title: str, text: str, reopen: bool, color: int = PopupConfig.default_color(), overwrite: bool = False):
        Popup(title, text, color, reopen=reopen, show=True, overwrite=overwrite)

    @staticmethod
    def generic_info(title: str, text: str):
        Popup.message(title, text, reopen=False)

    @staticmethod
    def examiner_says(text: str):
        Popup.message(Config.examiner_name(), text, reopen=True)

    @staticmethod
    def scientist_says(text: str):
        Popup.message(Config.scientist_name(), text, reopen=True)

    @staticmethod
    def npc_says(name: str, text: str):
        Popup.message(name, text, reopen=True)

    @staticmethod
    def from_message(message: Message, overwrite: bool = False):
        if Popup.__check_achievement:
            ret = message.get(Popup.__check_achievement)
            if ret:
                title, text = ret
                # the message is reopen-able because we explicitly defined it
                Popup.message(title, text, reopen=True, overwrite=overwrite)

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color(), show: bool = True,
                 overwrite: bool = False, reopen: bool = True):
        self.__title = title
        self.__text = text
        self.__color = color
        self.__reopen = reopen    # whether this popup should be reopen-able or not
        if show:
            self.show(overwrite)

    @property
    def _title(self) -> str:
        return self.__title

    @property
    def _text(self) -> str:
        return self.__text

    @property
    def _color(self) -> int:
        return self.__color

    @property
    def is_reopenable(self) -> bool:
        return self.__reopen

    def _base_show(self):
        Popup.__show_popup(self.__title, self.__text, self.__color)

    def _enqueue(self):
        Popup.__popup_queue.append(self)

    def show(self, overwrite: bool = False) -> None:
        if overwrite:
            Popup.__popup_queue.clear()
            Popup.__cur_popup = None
        if self.__cur_popup:
            self._enqueue()
        else:
            Popup.__cur_popup = self
            self._base_show()


class ConfirmationPopup(Popup):
    __show_popup = None

    @staticmethod
    def update_popup_function(show_popup_callback: Callable[[str, str, int, Callable[[bool], None]], None]):
        ConfirmationPopup.__show_popup = show_popup_callback

    @staticmethod
    def ask(title: str, text: str, callback: Callable[[bool], None]):
        ConfirmationPopup(title, text, callback)

    @staticmethod
    def scientist_asks(text: str, callback: Callable[[bool], None]):
        ConfirmationPopup(Config.scientist_name(), text, callback)

    def __init__(self, title: str, text: str, callback: Callable[[bool], None],
                 color: int = PopupConfig.default_color(), show: bool = True, overwrite: bool = False):
        self.__callback = callback
        super().__init__(title, text, color, show, overwrite, reopen=False)

    @property
    def _callback(self) -> Callable[[bool], None]:
        return self.__callback

    def _base_show(self) -> None:
        ConfirmationPopup.__show_popup(self._title, self._text, self._color, self._callback)


