import os.path

from game.controls import Controls, Keys
from util.config import PathConfig, GameplayConfig, Config


class KeyLogger:
    HEADER = "Qrogue "
    SEED_HEAD = "Seed="
    TIME_HEAD = "Time="
    CONFIG_HEAD = "[Config]"
    __BUFFER_SIZE = 1024
    __MIN_CONTENT_FOR_FLUSH = 167 + 20  # ~header size + minimum number of keystrokes to log
    __instance = None

    @staticmethod
    def instance() -> "KeyLogger":      # todo maybe choose a non-singelton pattern since it should be Run dependent?
        if KeyLogger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return KeyLogger.__instance

    @staticmethod
    def get_error_marker() -> str:
        return Keys.Invalid.to_char() + Keys.Invalid.to_char() + Keys.Invalid.to_char()

    def __init__(self, seed: int):
        if KeyLogger.__instance is not None:
            # happens if there was already another run before the current one
            #raise Exception("This class is a singleton!")
            KeyLogger.__instance.flush(force=True)
        self.__save_file, time = PathConfig.new_key_log_file(seed)
        self.__buffer = f"{KeyLogger.HEADER}{Config.version()}\n"
        self.__buffer += f"{KeyLogger.SEED_HEAD}{seed}\n"
        self.__buffer += f"{KeyLogger.TIME_HEAD}{time}\n\n"
        self.__buffer += f"{KeyLogger.CONFIG_HEAD}\n{GameplayConfig.to_file_text()}\n"

        # self.flush(force=True) # don't immediately flush to avoid generating files without meaningful content
        KeyLogger.__instance = self

    def log(self, controls: Controls, key_pressed: int):
        key = controls.encode(key_pressed)
        self.__buffer += key.to_char()

        self.flush(force=False)

    def log_error(self, message):
        self.__buffer += f"{KeyLogger.get_error_marker()}{message}{KeyLogger.get_error_marker()}"
        self.flush(force=True)  # errors are immediately flushed so we do not lose their information

    def flush_if_useful(self):
        """
        Flushes only if the .qrkl-file was already created (meaning we already flushed before) or if the buffer has a
        minimum length so we don't produce useless files (e.g. immediately quiting a run doesn't provide useful
        information).
        """
        if os.path.exists(self.__save_file) or len(self.__buffer) >= KeyLogger.__MIN_CONTENT_FOR_FLUSH:
            self.flush(force=True)

    def flush(self, force: bool):
        if force or len(self.__buffer) >= KeyLogger.__BUFFER_SIZE:
            PathConfig.write(self.__save_file, self.__buffer, may_exist=True, append=True)
            self.__buffer = ""
