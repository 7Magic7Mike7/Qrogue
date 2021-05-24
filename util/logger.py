from datetime import datetime

import py_cui.debug

from util.config import PathConfig
from util.key_logger import KeyLogger


class Logger(py_cui.debug.PyCUILogger):
    __BUFFER_SIZE = 2048
    __instance = None

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Logger.__instance

    def __init__(self, seed: int):
        super().__init__("Qrogue-Logger")
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__text = ""
            self.__message_popup = None
            self.__error_popup = None
            self.__save_file = PathConfig.new_log_file(seed)
            self.__buffer_size = 0
            self.__buffer = []
            Logger.__instance = self

    def set_popup(self, message_popup_function: "void(str, str)", error_popup_function: "void(str, str)") -> None:
        self.__message_popup = message_popup_function
        self.__error_popup = error_popup_function

    def __write(self, text) -> None:
        self.__buffer.append(text)
        self.__buffer_size += len(text)
        if self.__buffer_size >= Logger.__BUFFER_SIZE:
            self.flush()

    def info(self, message, **kwargs) -> None:
        time_str = datetime.now().strftime("%H-%M-%S")
        text = f"{time_str}: {message}"
        self.__write(text)

    def error(self, message, **kwargs) -> None:
        self.__error_popup("ERROR", message)
        try:
            if kwargs["only_popup"]:
                return
        except:
            pass
        highlighting = "\n----------------------------------\n"
        time_str = datetime.now().strftime("%H-%M-%S")
        text = f"{highlighting}{time_str}, Error: {message}{highlighting}"
        Logger.instance().__write(text)
        KeyLogger.instance().log_error(message)

    def print(self, message: str, clear: bool = False) -> None:
        print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        self.__message_popup("Logger", self.__text)

    def println(self, message: str = "", clear: bool = False) -> None:
        self.print(f"{message}\n", clear)

    def print_list(self, list=[], delimiter: str = ", ") -> None:
        sb = "["
        for elem in list:
            if elem is not None:
                sb += str(elem)
            sb += delimiter
        sb += "]"
        self.print(sb)

    def clear(self) -> None:
        self.__text = ""

    def flush(self) -> None:
        if self.__buffer_size > 0:
            text = ""
            for log in self.__buffer:
                text += log + "\n"
            PathConfig.write(self.__save_file, text, may_exist=True, append=True)
            self.__buffer = []
            self.__buffer_size = 0
