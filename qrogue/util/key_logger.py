import os.path
from typing import Optional, Callable

from qrogue.util import Logger, TestConfig, ErrorConfig
from qrogue.util.config import PathConfig, Config
from qrogue.util.controls import Controls, Keys


class KeyLogger:
    __BUFFER_SIZE = 1024
    __MIN_KEYSTROKES_FOR_FLUSH = 20  # minimum number of keystrokes to log      # todo: make value an Option?

    @staticmethod
    def get_error_marker() -> str:
        return Keys.ErrorMarker.to_char() + Keys.ErrorMarker.to_char() + Keys.ErrorMarker.to_char()

    def __init__(self, write: Optional[Callable[[str, str], None]] = None):
        self.__save_file: Optional[str] = None
        self.__buffer: Optional[str] = None
        self.__keystrokes = 0   # count how many keys are logged to not persist empty or almost empty runs

        if write is None: self.__write = lambda path, text: PathConfig.write(path, text, may_exist=True, append=True)
        else: self.__write = write

    def _is_for_levels(self) -> bool:
        return True

    @property
    def is_initialized(self) -> bool:
        return self.__save_file is not None and self.__buffer is not None

    def _append(self, character: str):
        self.__buffer += character

    def reinit(self, seed: int, level_name: str, save_state: str, save_path: Optional[str] = None):
        if self.is_initialized:
            # flush the old data if needed
            self.flush_if_useful()
        # start a new logging session
        if save_path is None: self.__save_file = PathConfig.new_key_log_file(seed, self._is_for_levels())
        else: self.__save_file = save_path
        self.__buffer = ""
        self._append(level_name)
        self._append("\n")
        self._append(Config.get_log_head(seed))
        self._append(save_state)
        self.__keystrokes = 0

    def log(self, controls: Controls, key_pressed: int):
        key = controls.encode(key_pressed)
        self._append(key.to_char())
        self.__keystrokes += 1
        self._flush(force=False)

    def log_error(self, message):
        self._append(f"{KeyLogger.get_error_marker()}{message}{KeyLogger.get_error_marker()}")
        self._flush(force=True)  # errors are immediately flushed, so we do not lose their information

    def flush_if_useful(self):
        """
        Flushes only if the .qrkl-file was already created (meaning we already flushed before) or if the buffer has a
        minimum length, so we don't produce useless files (e.g. immediately quiting a run doesn't provide useful
        information).
        """
        if os.path.exists(self.__save_file) or KeyLogger.__MIN_KEYSTROKES_FOR_FLUSH <= self.__keystrokes:
            self._flush(force=True)

    def _flush(self, force: bool):
        if Config.skip_persisting():
            return
        if force or len(self.__buffer) >= KeyLogger.__BUFFER_SIZE:
            self.__write(self.__save_file, self.__buffer)
            self.__buffer = ""


class OverWorldKeyLogger(KeyLogger):
    def __init__(self):
        super().__init__()

    def _is_for_levels(self) -> bool:
        return False

    def level_start(self, level_name: str):
        #self._append(
        #    f"{OverWorldKeyLogger.get_level_start_marker()}{level_name}{OverWorldKeyLogger.get_level_start_marker()}"
        #)
        pass
