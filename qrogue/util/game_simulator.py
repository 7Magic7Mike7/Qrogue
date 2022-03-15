from qrogue.util.config import PathConfig, GameplayConfig, Config
from qrogue.util.controls import Controls, Keys
from qrogue.util.key_logger import KeyLogger
from qrogue.util.logger import Logger


class GameSimulator:
    __ENCODING = "utf-8"
    __BUFFER_SIZE = 1024

    def __init__(self, controls: Controls, path: str, in_keylog_folder: bool = True, debug_print: bool = False):
        self.__controls = controls

        self.__reader = PathConfig.read_keylog_buffered(path, in_keylog_folder, buffer_size=GameSimulator.__BUFFER_SIZE)
        self.__cur_chunk = self.__next_chunk()
        # due to yield we don't immediately return None so self.__reader will not be None but self.__cur_chunk instead
        if self.__cur_chunk is None:
            Logger.instance().error("invalid path!")
            return
        self.__cur_index = -1
        self.__notification_popup = True

        # change the config so we can reproduce the run (e.g. different auto reset would destroy the simulation)
        if self.__cur_chunk.startswith(bytes(KeyLogger.HEADER, GameSimulator.__ENCODING)):
            version_start = len(KeyLogger.HEADER)
            version_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), version_start)
            self.__version = str(self.__cur_chunk[version_start:version_end], GameSimulator.__ENCODING)
            seed_start = self.__cur_chunk.index(bytes(KeyLogger.SEED_HEAD, GameSimulator.__ENCODING), version_end) \
                         + len(KeyLogger.SEED_HEAD)
            seed_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), seed_start)
            self.__seed = int(self.__cur_chunk[seed_start:seed_end])
            time_start = self.__cur_chunk.index(bytes(KeyLogger.TIME_HEAD, GameSimulator.__ENCODING), seed_end) \
                         + len(KeyLogger.TIME_HEAD)
            time_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), time_start)
            self.__time = str(self.__cur_chunk[time_start:time_end], GameSimulator.__ENCODING)

            start = self.__cur_chunk.index(bytes(KeyLogger.CONFIG_HEAD, GameSimulator.__ENCODING), seed_end) \
                    + len(KeyLogger.CONFIG_HEAD) + 1  # start at the first line after CONFIG_HEAD
            end = self.__cur_chunk.index(bytes("\n\n", GameSimulator.__ENCODING), start)
            config = str(self.__cur_chunk[start:end], GameSimulator.__ENCODING)
            GameplayConfig.from_log_text(config)

            # continue at the second \n because for next key we start with going to the next position
            self.__cur_index = end + 1

        if Config.debugging() and debug_print:
            print(self.__version)
            print(self.__seed)
            print(self.__time)
            print(GameplayConfig.to_file_text())
            print()
            print()
            print("Keys:")
            while self.next():
                pass
            print("finished")
            print()

    @property
    def version(self) -> str:
        return self.__version

    @property
    def seed(self) -> int:
        return self.__seed

    @property
    def time(self) -> str:
        return self.__time

    def __next_chunk(self) -> bytes:
        try:
            chunk = next(self.__reader)
            self.__cur_index = -1
            return bytes(chunk, GameSimulator.__ENCODING)
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
        if self.__notification_popup:
            self.__notification_popup = False
            return self.__controls.get_key(Keys.PopupClose)
        while self.__cur_chunk is not None:
            key = self.__next_key()
            if key > -1:
                return key
        return None
