import os.path

from qrogue.util.config import PathConfig, Config
from qrogue.util.controls import Controls, Keys


class KeyLogger:
    __BUFFER_SIZE = 1024
    __MIN_CONTENT_FOR_FLUSH = 167 + 20  # ~header size + minimum number of keystrokes to log

    @staticmethod
    def get_error_marker() -> str:
        return Keys.Invalid.to_char() + Keys.Invalid.to_char() + Keys.Invalid.to_char()

    def __init__(self, seed: int):
        self.__save_file = PathConfig.new_key_log_file(seed)
        self.__buffer = Config.get_log_head(seed)

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
