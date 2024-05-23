from typing import Callable, Optional, List, Union

from py_cui.debug import PyCUILogger

from .config import Config, ErrorConfig, PathConfig, TestConfig
from .util_functions import cur_datetime


class Logger(PyCUILogger):
    __BUFFER_SIZE = 4096
    __instance = None

    @staticmethod
    def print_to_console(message: str) -> None:
        time_str = cur_datetime().strftime("%H-%M-%S")
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
            if Logger.__instance is None: return
            Logger.__instance.flush()   # flush before we reset to not lose data
            Logger.__instance = None
        else:
            raise TestConfig.StateException(ErrorConfig.singleton_reset("Logger"))

    @staticmethod
    def _set_instance(logger: "Logger"):
        # needed to insert a special TestLogger during testing
        Logger.__instance = logger

    def __init__(self, commit: Optional[Callable[[str], None]] = None):
        super().__init__("Qrogue-Logger")
        if Logger.__instance is not None:
            Logger.__instance.throw(Exception(ErrorConfig.singleton("Logger")))
        else:
            if commit is None:
                save_file = PathConfig.new_log_file()

                def commit_(text: str):
                    PathConfig.write(save_file, text, may_exist=True, append=True)
                self.__commit = commit_
            else:
                self.__commit = commit

            self.__text = ""
            self.__error_popup: Optional[Callable[[str], None]] = None
            self.__buffer: List[str] = []   # stores logged lines
            self.__error_counter = 0
            Logger.__instance = self

    @property
    def __buffer_size(self) -> int:
        """
        Returns: number of characters stored in buffer
        """
        return sum([len(line) for line in self.__buffer])

    @property
    def error_count(self) -> int:
        return self.__error_counter

    def set_popup(self, error_popup_function: Callable[[str], None]) -> None:
        self.__error_popup = error_popup_function

    def _write(self, text: str, from_pycui: Optional[bool]) -> None:
        """
        Args:
            text: the text to write to buffer
            from_pycui: True if text comes from PyCUI, False if it comes from QRogue, None if we do not know (e.g.,
                        some Exceptions)
        """
        self.__buffer.append(text)
        if self.__buffer_size >= Logger.__BUFFER_SIZE:
            self.flush()

    def info(self, message, from_pycui: bool = True, **kwargs) -> None:
        time_str = cur_datetime().strftime("%H-%M-%S")
        if from_pycui:
            self._write(f"{{PyCUI}}{time_str}: {message}", True)
        else:
            text = f"{{Qrogue}}{time_str}: {message}"
            self._write(text, False)
            if Config.debugging(): print(text)

    def debug(self, msg: str, from_pycui: bool = True, *args, **kwargs) -> None:
        if from_pycui and msg.startswith("Generated fragments"): return
        if Config.debugging():
            self.info(f"{{DEBUG}} |{msg}", from_pycui=from_pycui)

    def warn(self, msg: str, from_pycui: bool = True, *args, **kwargs) -> None:
        highlighting = "\n----------------------------------\n"
        self.info(f"{highlighting}WARNING |{msg}{highlighting}", from_pycui=from_pycui)

    def assertion(self, statement: bool, message, show_popup: bool = False):
        if Config.debugging():
            assert statement, str(message)
        else:
            if not statement:
                self.error(message, show_popup, from_pycui=False)

    def error(self, message, show: bool = True, from_pycui: bool = True, **kwargs) -> None:
        self.__error_counter += 1
        if show:
            self.__error_popup(str(message))
        highlighting = "\n----------------------------------\n"
        self.info(f"{highlighting}ERROR |{message}{highlighting}", from_pycui=from_pycui)

    def throw(self, error: Union[BaseException, str]) -> None:
        if isinstance(error, str):
            error = Exception(error)
        self.__error_counter += 1
        print(error)
        self._write(f"[ERROR] {error}", None)
        self.flush()
        raise error

    def clear(self) -> None:
        self.__text = ""

    def flush(self) -> None:
        if self.__buffer_size > 0:
            text = ""
            for log in self.__buffer:
                text += log + "\n"
            self.__commit(text)
            self.__buffer.clear()
