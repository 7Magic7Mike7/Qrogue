import os.path

from qrogue.util import Logger
from qrogue.util.config import PathConfig, Config
from qrogue.util.controls import Controls, Keys


class KeyLogger:
    __BUFFER_SIZE = 1024
    __MIN_CONTENT_FOR_FLUSH = 180 + 20  # ~header and level name size + minimum number of keystrokes to log

    @staticmethod
    def get_error_marker() -> str:
        return Keys.ErrorMarker.to_char() + Keys.ErrorMarker.to_char() + Keys.ErrorMarker.to_char()

    def __init__(self):
        self.__save_file = None
        self.__buffer = None

    def _is_for_levels(self) -> bool:
        return True

    @property
    def is_initialized(self) -> bool:
        return self.__save_file and self.__buffer

    def _append(self, character: str):
        self.__buffer += character

    def reinit(self, seed: int, level_name: str):
        if self.is_initialized:
            # flush the old data if needed
            self.flush_if_useful()
        # start a new logging session
        self.__save_file = PathConfig.new_key_log_file(seed, self._is_for_levels())
        self.__buffer = ""
        self._append(level_name)
        self._append("\n")
        self._append(Config.get_log_head(seed))

    def log(self, controls: Controls, key_pressed: int):
        key = controls.encode(key_pressed)
        self._append(key.to_char())
        self._flush(force=False)

    def log_error(self, message):
        self._append(f"{KeyLogger.get_error_marker()}{message}{KeyLogger.get_error_marker()}")
        self._flush(force=True)  # errors are immediately flushed so we do not lose their information

    def flush_if_useful(self):
        """
        Flushes only if the .qrkl-file was already created (meaning we already flushed before) or if the buffer has a
        minimum length so we don't produce useless files (e.g. immediately quiting a run doesn't provide useful
        information).
        """
        if os.path.exists(self.__save_file) or len(self.__buffer) >= KeyLogger.__MIN_CONTENT_FOR_FLUSH:
            self._flush(force=True)

    def _flush(self, force: bool):
        if force or len(self.__buffer) >= KeyLogger.__BUFFER_SIZE:
            PathConfig.write(self.__save_file, self.__buffer, may_exist=True, append=True)
            self.__buffer = ""


class OverWorldKeyLogger(KeyLogger):
    __instance = None

    @staticmethod
    def instance() -> "OverWorldKeyLogger":
        if OverWorldKeyLogger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return OverWorldKeyLogger.__instance

    def __init__(self):
        if OverWorldKeyLogger.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            super().__init__()
            OverWorldKeyLogger.__instance = self

    def _is_for_levels(self) -> bool:
        return False

    def level_start(self, level_name: str):
        #self._append(
        #    f"{OverWorldKeyLogger.get_level_start_marker()}{level_name}{OverWorldKeyLogger.get_level_start_marker()}"
        #)
        pass
