from game.controls import Controls
from util.config import PathConfig, GameplayConfig
from util.key_logger import KeyLogger
from util.logger import Logger


class GameSimulator:
    __BUFFER_SIZE = 1024

    def __init__(self, controls: Controls, path: str, in_keylog_folder: bool = True):
        self.__controls = controls

        self.__reader = PathConfig.read_keylog_buffered(path, in_keylog_folder, buffer_size=GameSimulator.__BUFFER_SIZE)
        self.__cur_chunk = self.__next_chunk()
        # due to yield we don't immediately return None so self.__reader will not be None but self.__cur_chunk instead
        if self.__cur_chunk is None:
            Logger.instance().error("invalid path!")
            return
        self.__cur_index = -1

        # change the config so we can reproduce the run (e.g. different auto reset would destroy the simulation)
        if self.__cur_chunk.startswith(bytes(KeyLogger.CONFIG_HEAD, "utf-8")):
            start = self.__cur_chunk.index(bytes("\n", "utf-8")) + 1
            end = self.__cur_chunk.index(bytes("\n\n", "utf-8"), start)
            config = str(self.__cur_chunk[start:end], "UTF-8")
            GameplayConfig.from_log_text(config)

            self.__cur_index = end  # continue at \n because for next key we start with going to the next position

    def __next_chunk(self) -> bytes:
        try:
            chunk = next(self.__reader)
            self.__cur_index = -1
            return bytes(chunk, "utf-8")
        except StopIteration:
            return None

    def __next_key(self) -> int:
        """

        :return: the next key or -1 if we should retry (self.__cur_chunk is None if we reached the end)
        """
        self.__cur_index += 1
        if 0 <= self.__cur_index < len(self.__cur_chunk):
            code = self.__cur_chunk[self.__cur_index]
            key = self.__controls.decode(code)
            if key:
                return key
        else:
            self.__cur_chunk = self.__next_chunk()
        return -1

    def next(self) -> int:
        """

        :return: the key to press or None if the simulation finished
        """
        while self.__cur_chunk is not None:
            key = self.__next_key()
            if key > -1:
                return key
        return None
