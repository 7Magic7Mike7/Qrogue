from datetime import datetime
from typing import Callable, Optional, List, Union

from py_cui.debug import PyCUILogger

from qrogue.util import PyCuiColors, TestConfig, ErrorConfig
from qrogue.util.config import PathConfig, Config


class Logger(PyCUILogger):
    __BUFFER_SIZE = 2048
    __instance = None

    @staticmethod
    def print_to_console(message: str) -> None:
        time_str = datetime.now().strftime("%H-%M-%S")
        text = f"{{Qrogue}}{time_str}: {message}"
        print(text)

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception(ErrorConfig.singleton_no_init("Logger"))
        return Logger.__instance

    @staticmethod
    def reset():
        if TestConfig.is_active():
            Logger.__instance = None
        else:
            raise TestConfig.StateException(ErrorConfig.singleton_reset("Logger"))

    def __init__(self, seed: int, commit: Optional[Callable[[str], None]] = None):
        super().__init__("Qrogue-Logger")
        if Logger.__instance is not None:
            Logger.__instance.throw(Exception(ErrorConfig.singleton("Logger")))
        else:
            if commit is None:
                save_file = PathConfig.new_log_file(seed)

                def commit_(text: str):
                    PathConfig.write(save_file, text, may_exist=True, append=True)
                self.__commit = commit_
            else:
                self.__commit = commit

            self.__text = ""
            self.__message_popup: Optional[Callable[[str, str, int], None]] = None
            self.__error_popup: Optional[Callable[[str, str], None]] = None
            self.__buffer: List[str] = [Config.get_log_head(seed)]
            self.__error_counter = 0
            Logger.__instance = self

    @property
    def __buffer_size(self) -> int:
        return len(self.__buffer)

    @property
    def error_count(self) -> int:
        return self.__error_counter

    def set_popup(self, message_popup_function: Callable[[str, str, int], None],
                  error_popup_function: Callable[[str, str], None]) -> None:
        self.__message_popup = message_popup_function
        self.__error_popup = error_popup_function

    def __write(self, text) -> None:
        self.__buffer.append(text)
        if self.__buffer_size >= Logger.__BUFFER_SIZE:
            self.flush()

    def info(self, message, from_pycui: bool = True, **kwargs) -> None:
        time_str = datetime.now().strftime("%H-%M-%S")
        if from_pycui:
            self.__write(f"{{PyCUI}}{time_str}: {message}")
        else:
            text = f"{{Qrogue}}{time_str}: {message}"
            self.__write(text)
            if Config.debugging(): print(text)

    def debug(self, msg: str, from_pycui: bool = True, *args, **kwargs) -> None:
        if from_pycui and msg.startswith("Generated fragments"): return
        if Config.debugging():
            self.info(f"{{DEBUG}} |{msg}", from_pycui=from_pycui)

    def warn(self, msg: str, from_pycui: bool = True, *args, **kwargs) -> None:
        highlighting = "\n----------------------------------\n"
        self.info(f"{highlighting}WARNING |{msg}{highlighting}", from_pycui=from_pycui)

    def show_error(self, message) -> None:
        self.__error_counter += 1
        self.__error_popup("ERROR", str(message))

    def assertion(self, statement: bool, message, show_popup: bool = False):
        if Config.debugging():
            assert statement, str(message)
        else:
            if not statement:
                self.error(message, show_popup, False)

    def error(self, message, show: bool = True, from_pycui: bool = True, **kwargs) -> None:
        self.__error_counter += 1
        if show:
            self.__error_popup("ERROR", str(message))
        highlighting = "\n----------------------------------\n"
        self.info(f"{highlighting}ERROR |{message}{highlighting}", from_pycui=from_pycui)

    def throw(self, error: Union[BaseException, str]) -> None:
        if isinstance(error, str):
            error = Exception(error)
        self.__error_counter += 1
        print(error)
        self.__write(f"[ERROR] {error}")
        self.flush()
        raise error

    def println(self, message: str = "", clear: bool = False) -> None:
        message = f"{message}\n"
        if Config.debugging(): print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        self.__message_popup("Logger", self.__text, PyCuiColors.WHITE_ON_CYAN)

    def clear(self) -> None:
        self.__text = ""

    def flush(self) -> None:
        if self.__buffer_size > 0:
            text = ""
            for log in self.__buffer:
                text += log + "\n"
            self.__commit(text)
            self.__buffer = []
