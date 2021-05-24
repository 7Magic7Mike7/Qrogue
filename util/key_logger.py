from game.controls import Controls, Keys
from util.config import PathConfig, GameplayConfig


class KeyLogger:
    CONFIG_HEAD = "[Config]"
    __BUFFER_SIZE = 1024
    __instance = None

    @staticmethod
    def instance() -> "KeyLogger":
        if KeyLogger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return KeyLogger.__instance

    @staticmethod
    def get_error_marker() -> str:
        return Keys.Invalid.to_char() + Keys.Invalid.to_char() + Keys.Invalid.to_char()

    def __init__(self):
        if KeyLogger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__save_file = PathConfig.new_key_log_file()
            self.__buffer = f"{KeyLogger.CONFIG_HEAD}\n{GameplayConfig.to_file_text()}\n"
            self.flush(force=True)
            KeyLogger.__instance = self

    def log(self, controls: Controls, key_pressed: int):
        key = controls.encode(key_pressed)
        self.__buffer += key.to_char()

        if len(self.__buffer) >= KeyLogger.__BUFFER_SIZE:
            self.flush(force=True)

    def log_error(self, message):
        self.__buffer += f"{KeyLogger.get_error_marker()}{message}{KeyLogger.get_error_marker()}"

    def flush(self, force: bool):
        if force or len(self.__buffer) > 0:
            PathConfig.write(self.__save_file, self.__buffer, may_exist=True, append=True)
            self.__buffer = ""
