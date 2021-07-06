
from py_cui.widgets import BlockLabel

class Logger:
    def __init__(self, label: BlockLabel):
        self.__label = label
        self.__text = ""

    def print(self, message: str):
        print(message)
        self.__text += message
        self.__label.set_title(self.__text)

    def println(self, message=""):
        self.print(message + "\n")  # TODO use system dependent new line?

    def print_list(self, list=[], delimiter: str = ", "):
        sb = ""
        for elem in list:
            if elem is not None:
                sb += elem.__str__()
            sb += delimiter
        return sb

    def clear(self):
        self.__text = ""
        self.print("")
