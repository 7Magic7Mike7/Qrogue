from enum import IntEnum
from typing import Callable, Optional, List, Tuple

from qrogue.game.logic import Message
from qrogue.util import Config, PopupConfig, Logger, HelpText


class Popup:
    class Pos(IntEnum):
        Center = 0
        Top = 1
        TopRight = 2
        Right = 3
        BottomRight = 4
        Bottom = 5
        BottomLeft = 6
        Left = 7
        TopLeft = 8

        Matrix = 9

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

    # dimensions are without padding, so purely the size of the content part of a Popup
    DimWidth = Dimension(40, 70, 104, 140)
    DimHeight = Dimension(3, 5, 8, 13)

    __DEFAULT_POS = PopupConfig.default_position()
    __show_popup: Optional[Callable[[str, str, int, int, Optional[Tuple[int, int]], Optional[bool], Optional[int],
                                     Optional[PopupConfig.Importance]],
                                    None]] = None
    __check_achievement_callback: Optional[Callable[[str], bool]] = None
    __popup_queue: List["Popup"] = []
    __cur_popup: Optional["Popup"] = None

    @staticmethod
    def is_initialized() -> bool:
        return Popup.__show_popup is not None and Popup.__check_achievement_callback is not None

    @staticmethod
    def update_popup_functions(show_popup_callback: Callable[[str, str, int, int, Optional[Tuple[int, int]],
                                                              Optional[bool], Optional[int]], None]) -> None:
        """
        callable(title, text, color, position, dimensions, reopen, padding x)
        """
        Popup.__show_popup = show_popup_callback

    @staticmethod
    def update_check_achievement_function(check_achievement_callback: Callable[[str], bool]) -> None:
        Popup.__check_achievement_callback = check_achievement_callback

    @staticmethod
    def reset_queue():
        Popup.__popup_queue.clear()

    @staticmethod
    def on_close() -> bool:
        if Popup.__cur_popup is not None:
            Popup.__cur_popup.on_close_callback()
            Popup.__cur_popup.__on_close_callback = None  # clear callback to not execute it when reopening!
        Popup.__cur_popup = None
        if len(Popup.__popup_queue) > 0:
            next_popup = Popup.__popup_queue.pop(0)
            next_popup.show()
            return False  # don't fully close popup
        return True  # popup no longer needed so we can fully close it

    @staticmethod
    def message(title: str, text: str, reopen: bool, pos: Optional[int] = None,
                color: int = PopupConfig.default_color(), overwrite: bool = False,
                on_close_callback: Callable[[], None] = None,
                dimensions: Optional[Tuple[int, int]] = None,
                importance: Optional[PopupConfig.Importance] = None):
        if pos is None:
            pos = Popup.__DEFAULT_POS
        if importance is None:
            importance = PopupConfig.Importance.Undefined
        Popup(title, text, pos, color, reopen=reopen, show=True, overwrite=overwrite,
              on_close_callback=on_close_callback, dimensions=dimensions, importance=importance)

    @staticmethod
    def generic_info(title: str, text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = False
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(title, text, reopen=reopen, pos=pos, importance=PopupConfig.Importance.Info)

    @staticmethod
    def show_help(help_text: HelpText):
        Popup.generic_info(help_text.name, help_text.text)

    @staticmethod
    def error(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None, overwrite: bool = True,
              log_error: bool = True, add_report_note: bool = False):
        """
        Args:
            text: a text describing the error
            reopen: whether the popup should be reopen-able (defaults to False)
            pos: position of the popup
            overwrite: whether this popup should overwrite the currently displayed one if there is any (defaults to True)
            log_error: whether we should forward the error to our Logger (defaults to True)
            add_report_note: whether to add a text to inform the player how to report the error
        """
        if reopen is None:
            reopen = False
        if pos is None:
            pos = Popup.__DEFAULT_POS
        if log_error: Logger.instance().error(text, show=False, from_pycui=False)
        if add_report_note:
            text += f"\nPlease report this error together with your user data to {Config.report_address()}"
        Popup.message("Error", text, reopen, pos, overwrite=overwrite, importance=PopupConfig.Importance.Error)

    @staticmethod
    def system_says(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(Config.system_name(), text, reopen=reopen, pos=pos, importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def examiner_says(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(Config.examiner_name(), text, reopen=reopen, pos=pos, importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def scientist_says(text: str, reopen: Optional[bool] = None, pos: Optional[int] = None,
                       dimensions: Optional[Tuple[int, int]] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(Config.scientist_name(), text, reopen=reopen, pos=pos, dimensions=dimensions,
                      importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def npc_says(name: str, text: str, reopen: Optional[bool] = None, pos: Optional[int] = None):
        if reopen is None:
            reopen = True
        if pos is None:
            pos = Popup.__DEFAULT_POS
        Popup.message(name, text, reopen=reopen, pos=pos, importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def from_message(message: Message, overwrite: bool = False):
        if Popup.__check_achievement_callback:
            ret = message.get(Popup.__check_achievement_callback)  # resolve possible alternative messages
            if ret is not None:
                title, text = ret
                reopen = message.priority
                Popup.message(title, text, reopen=reopen, pos=message.position, overwrite=overwrite,
                              importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def from_message_trigger(message: Message, on_close_callback: Callable[[], None]):
        if Popup.__check_achievement_callback:
            ret = message.get(Popup.__check_achievement_callback)  # resolve possible alternative messages
            if ret is not None:
                title, text = ret
                if Config.debugging():
                    title += f" {{@*{message.id}}}"
                reopen = message.priority
                Popup.message(title, text, reopen, pos=message.position, on_close_callback=on_close_callback,
                              importance=PopupConfig.Importance.Dialogue)

    @staticmethod
    def show_matrix(title: str, text: str, prefix: str = ""):
        # remove the additional whitespace at the end of a line (needed for CircuitMatrixWidget to center correctly,
        # but not here since a popup is left-aligned [although we are technically centered since we fit the width])
        lines = [line.rstrip(' ') for line in text.splitlines(keepends=False)]
        height = len(lines)
        width = max([len(line) for line in lines])
        Popup(title, prefix + "\n".join(lines), Popup.Pos.Matrix, PopupConfig.default_color(), reopen=False, show=True,
              overwrite=False, on_close_callback=None, dimensions=(height, width), padding_x=0,
              importance=PopupConfig.Importance.Info)

    def __init__(self, title: str, text: str, position: int, color: int = PopupConfig.default_color(),
                 show: bool = True, overwrite: bool = False, reopen: bool = True,
                 on_close_callback: Callable[[], None] = None, dimensions: Optional[Tuple[int, int]] = None,
                 padding_x: Optional[int] = None,
                 importance: PopupConfig.Importance = PopupConfig.Importance.Undefined):
        self.__title = title
        self.__text = text
        self.__position = position
        self.__dimensions = dimensions
        self.__padding_x = padding_x
        self.__importance = importance
        self.__color = color
        self.__reopen = reopen  # whether this popup should be reopen-able or not
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
        Popup.__show_popup(self.__title, self.__text, self.__position, self.__color, self.__dimensions, self.__reopen,
                           self.__padding_x, self.__importance)

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
    __DEFAULT_POS = PopupConfig.default_position()
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
        def on_close():
            callback(self.__confirmed)

        self.__answers = answers
        super().__init__(title, text, position, color, show, overwrite, reopen=False,
                         on_close_callback=on_close)
        self.__confirmed: Optional[int] = None

    def __set_confirmation(self, confirmed: int):
        # by setting confirmed here we determine the parameter of the callback called after closing
        self.__confirmed = confirmed

    def _base_show(self) -> None:
        ConfirmationPopup.__show_popup(self._title, self._text, self._color, self.__set_confirmation, self.__answers)
