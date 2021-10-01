
class Logger:
    __instance = None

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Logger.__instance

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__text = ""
            self.__message_popup = None
            self.__error_popup = None
            Logger.__instance = self

    def set_popup(self, message_popup_function: "void(str, str)", error_popup_function: "void(str, str)"):
        self.__message_popup = message_popup_function
        self.__error_popup = error_popup_function

    def info(self, message):
        pass

    def error(self, message):
        self.__error_popup("ERROR", message)

    def print(self, message: str, clear: bool = False):
        print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        self.__message_popup("Logger", self.__text)

    def println(self, message: str = "", clear: bool = False):
        self.print(f"{message}\n", clear)

    def print_list(self, list=[], delimiter: str = ", "):
        sb = "["
        for elem in list:
            if elem is not None:
                sb += str(elem)
            sb += delimiter
        sb += "]"
        self.print(sb)

    def clear(self):
        self.__text = ""
