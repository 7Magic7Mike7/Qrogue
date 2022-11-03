from typing import Callable, Optional, List, Tuple

from qrogue.game.logic import Message
from qrogue.util import Config, PopupConfig


class Popup:
    class Pos:
        Center = 0
        Top = 1
        TopRight = 2
        Right = 3
        BottomRight = 4
        Bottom = 5
        BottomLeft = 6
        Left = 7
        TopLeft = 8

    class Dimension:
        def __init__(self, tiny: int, small: int, medium: int, large: int):
            self.__tiny = tiny
            self.__small = small
            self.__medium = medium
            self.__large = large

        @property
        def tiny(self) -> int:
            return self.__tiny

        @property
        def small(self) -> int:
            return self.__small

        @property
        def medium(self) -> int:
            return self.__medium

        @property
        def large(self) -> int:
            return self.__large

    DimX = Dimension(50, 80, 114, 150)
    DimY = Dimension(5, 7, 10, 15)

    __DEFAULT_POS = PopupConfig.default_pos()
    __show_popup: Optional[Callable[[str, str, int, int, Optional[Tuple[int, int]]], None]] = None
    __check_achievement: Optional[Callable[[str], bool]] = None
    __popup_queue: List["Popup"] = []
    __cur_popup: Optional["Popup"] = None
    __last_popup: Optional["Popup"] = None

    @staticmethod
    def update_popup_functions(show_popup_callback: Callable[[str, str, int, int, Optional[Tuple[int, int]]], None]) \
            -> None:
        Popup.__show_popup = show_popup_callback

    @staticmethod
    def update_check_achievement_function(check_achievement_callback: Callable[[str], bool]) -> None:
        Popup.__check_achievement = check_achievement_callback

    @staticmethod
    def clear_last_popup() -> None:
        Popup.__last_popup = None

    @staticmethod
    def on_close() -> bool:
        if Popup.__cur_popup:
            Popup.__cur_popup.on_close_callback()
            Popup.__cur_popup.__on_close_callback = None    # clear callback to not execute it when reopening!
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
    def message(title: str, text: str, reopen: bool, pos: Optional[int] = None,
                color: int = PopupConfig.default_color(), overwrite: bool = False,
                on_close_callback: Callable[[], None] = None,
                dimensions: Optional[Tuple[int, int]] = None):
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup(title, text, pos, color, reopen=reopen, show=True, overwrite=overwrite,
              on_close_callback=on_close_callback, dimensions=dimensions)

    @staticmethod
    def generic_info(title: str, text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = False
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(title, text, reopen=reopen, pos=pos)

    @staticmethod
    def examiner_says(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(Config.examiner_name(), text, reopen=reopen, pos=pos)

    @staticmethod
    def scientist_says(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None,
                       dimensions: Optional[Tuple[int, int]] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(Config.scientist_name(), text, reopen=reopen, pos=pos, dimensions=dimensions)

    @staticmethod
    def npc_says(name: str, text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(name, text, reopen=reopen, pos=pos)

    @staticmethod
    def from_message(message: Message, overwrite: bool = False):
        if Popup.__check_achievement:
            ret = message.get(Popup.__check_achievement)    # resolve possible alternative messages
            if ret:
                title, text = ret
                reopen = True
                # the popup is not reopenable if it has lower priority than the last popup
                if Popup.__last_popup is not None and Popup.__last_popup.is_reopenable and not message.priority:
                    reopen = False
                Popup.message(title, text, reopen=reopen, pos=message.position, overwrite=overwrite)

    @staticmethod
    def from_message_trigger(message: Message, on_close_callback: Callable[[], None]):
        if Popup.__check_achievement:
            ret = message.get(Popup.__check_achievement)    # resolve possible alternative messages
            if ret is not None:
                title, text = ret
                if Config.debugging():
                    title += f" {{@*{message.id}}}"
                reopen = True
                # the popup is not reopenable if it has lower priority than the last popup
                if Popup.__last_popup is not None and Popup.__last_popup.is_reopenable and not message.priority:
                    reopen = False
                Popup.message(title, text, reopen, pos=message.position, on_close_callback=on_close_callback)

    def __init__(self, title: str, text: str, position: int, color: int = PopupConfig.default_color(),
                 show: bool = True, overwrite: bool = False, reopen: bool = True,
                 on_close_callback: Callable[[], None] = None, dimensions: Optional[Tuple[int, int]] = None):
        self.__title = title
        self.__text = text
        self.__position = position
        self.__dimensions = dimensions
        self.__color = color
        self.__reopen = reopen    # whether this popup should be reopen-able or not
        self.__on_close_callback = on_close_callback
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

    def on_close_callback(self):
        if self.__on_close_callback:
            self.__on_close_callback()

    def _base_show(self):
        Popup.__show_popup(self.__title, self.__text, self.__position, self.__color, self.__dimensions)

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
    __DEFAULT_POS = PopupConfig.default_pos()
    __show_popup: Callable[[str, str, int, Callable[[int], None], Optional[List[str]]], None] = None

    @staticmethod
    def update_popup_function(show_popup_callback: Callable[[str, str, int, Callable[[int], None], Optional[List[str]]],
                                                            None]):
        ConfirmationPopup.__show_popup = show_popup_callback

    @staticmethod
    def ask(title: str, text: str, callback: Callable[[int], None], answers: Optional[List[str]] = None):
        ConfirmationPopup(title, text, callback, answers)

    def __init__(self, title: str, text: str, callback: Callable[[int], None], answers: Optional[List[str]] = None,
                 position: int = __DEFAULT_POS, color: int = PopupConfig.default_color(), show: bool = True,
                 overwrite: bool = False):
        def on_close_callback():
            callback(self.__confirmed)
        self.__answers = answers
        super().__init__(title, text, position, color, show, overwrite, reopen=False,
                         on_close_callback=on_close_callback)
        self.__confirmed: Optional[int] = None

    def __set_confirmation(self, confirmed: int):
        # by setting confirmed here we determine the parameter of the callback called after closing
        self.__confirmed = confirmed

    def _base_show(self) -> None:
        ConfirmationPopup.__show_popup(self._title, self._text, self._color, self.__set_confirmation, self.__answers)
