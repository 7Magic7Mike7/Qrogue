
from py_cui.widgets import BlockLabel


class Logger:
    __instance = None

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__label = None
            self.__info_counter = 0
            self.__text = ""
            Logger.__instance = self

    def set_label(self, label: BlockLabel):
        self.__label = label
        self.print("", clear=False)  # update the text of the newly set label

    def info(self, message):
        self.__info_counter += 1
        if self.__info_counter % 100 == 0:
            print(f"INFO[{self.__info_counter:03f}]: {message}")

    def print(self, message: str, clear: bool = False):
        print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        if self.__label is not None:
            self.__label.set_title(self.__text)

    def println(self, message: str = "", clear: bool = False):
        self.print(f"{message}\n", clear)

    def print_list(self, list=[], delimiter: str = ", "):
        sb = "["
        for elem in list:
            if elem is not None:
                sb += elem.__str__()
            sb += delimiter
        sb += "]"
        self.print(sb)

    def clear(self):
        self.__text = ""
        self.print("")

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Logger.__instance
