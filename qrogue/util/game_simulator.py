from typing import Tuple, Optional

from qrogue.util import Logger
from qrogue.util.achievements import Unlocks
from qrogue.util.config import PathConfig, GameplayConfig, Config, ColorConfig, FileTypes
from qrogue.util.controls import Controls, Keys


class GameSimulator:
    # naming convention:
    #   - raw key = PyCUI-internal representation of the physically pressed key
    #   - logical key = QRogue-internal representation of the logically pressed key (e.g., MoveUp, SelectionUp)
    #       ~ multiple logical keys can correspond to the same raw key, both situationally (overlapping controls) and
    #         permanently (same controls)
    #   - key code = "translator" between raw and logical keys
    #       ~ Corresponds to the integer value of a logical key, but as it is computed from raw keys it might not be
    #         the same as its original logical counterpart. However, when given the same Controls-object, it will always
    #         be equivalent to its original logical key.

    __ENCODING = "utf-8"
    __BUFFER_SIZE = 1024

    def __init__(self, path: str, in_keylog_folder: bool = True):
        if not path.endswith(FileTypes.KeyLog.value):
            path += FileTypes.KeyLog.value

        self.__controls: Optional[Controls] = None
        self.__reader = PathConfig.read_keylog_buffered(path, in_keylog_folder, buffer_size=GameSimulator.__BUFFER_SIZE)
        self.__cur_chunk: Optional[bytes] = None
        self._next_chunk()  # initializes __cur_chunk

        self.__notification_popup = True
        self.__marker_counter = 0
        self.__finished = False

        # retrieve the name of the map that was played
        second_line = self.__cur_chunk.index((bytes("\n", GameSimulator.__ENCODING)))
        self.__map_name = str(self.__cur_chunk[0:second_line], GameSimulator.__ENCODING)
        self.__cur_index = second_line

        # change the config so we can reproduce the run (e.g. different auto reset would destroy the simulation)
        if self.__cur_chunk[second_line + 1:].startswith(bytes(Config.HEADER(), GameSimulator.__ENCODING)):
            version_start = second_line + len(Config.HEADER())
            version_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), version_start)
            self.__version = str(self.__cur_chunk[version_start:version_end], GameSimulator.__ENCODING)
            seed_start = self.__cur_chunk.index(bytes(Config.SEED_HEAD(), GameSimulator.__ENCODING), version_end) \
                + len(Config.SEED_HEAD())
            seed_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), seed_start)
            self.__seed = int(self.__cur_chunk[seed_start:seed_end])
            time_start = self.__cur_chunk.index(bytes(Config.TIME_HEAD(), GameSimulator.__ENCODING), seed_end) \
                + len(Config.TIME_HEAD())
            time_end = self.__cur_chunk.index(bytes("\n", GameSimulator.__ENCODING), time_start)
            self.__time = str(self.__cur_chunk[time_start:time_end], GameSimulator.__ENCODING)

            start = self.__cur_chunk.index(bytes(Config.CONFIG_HEAD(), GameSimulator.__ENCODING), seed_end) \
                + len(Config.CONFIG_HEAD()) + 1  # start at the first line after CONFIG_HEAD
            end = self.__cur_chunk.index(bytes("\n\n", GameSimulator.__ENCODING), start)
            config = str(self.__cur_chunk[start:end], GameSimulator.__ENCODING)
            GameplayConfig.from_log_text(config)

            # todo: use constants instead of these strings
            start = self.__cur_chunk.index(bytes("Qrogue<", GameSimulator.__ENCODING), end)
            if start < 0:
                self.__save_state = None
            else:
                end = self.__cur_chunk.index(bytes(">Qrogue", GameSimulator.__ENCODING), start) + len(">Qrogue")
                self.__save_state = str(self.__cur_chunk[start:end], GameSimulator.__ENCODING)

            # continue at the \n at the end of the save state because in next_key() we start with going to the next position
            self.__cur_index = end
        else:
            self.__version = "???"
            self.__seed = -1
            self.__time = "???"

    @property
    def map_name(self) -> str:
        return self.__map_name

    @property
    def simulates_over_world(self) -> bool:
        return self.__map_name == "meta"

    @property
    def version(self) -> str:
        return self.__version

    @property
    def seed(self) -> int:
        return self.__seed

    @property
    def time(self) -> str:
        return self.__time

    @property
    def save_state(self) -> Optional[str]:
        return self.__save_state

    def set_controls(self, controls: Controls):
        self.__controls = controls

    def _next_chunk(self):
        chunk = next(self.__reader)
        self.__cur_index = -1
        self.__cur_chunk = bytes(chunk, GameSimulator.__ENCODING)

    def __next_key(self) -> int:
        """

        :return: the next (raw) key or -1 if we should retry (self.__cur_chunk is None if we reached the end)
        """
        self.__cur_index += 1
        if 0 <= self.__cur_index < len(self.__cur_chunk):
            code = self.__cur_chunk[self.__cur_index]
            key_pressed, key = self.__controls.decode(code)
            if key is Keys.ErrorMarker:
                self.__marker_counter += 1
                if self.__marker_counter >= 3:  # todo fix magic number
                    pass  # todo parse error
                return -1
            else:
                self.__marker_counter = 0
            if key_pressed:
                return key_pressed
        else:
            try:
                self._next_chunk()
            except StopIteration:
                self.__cur_chunk = None
        return -1

    def next(self) -> Optional[int]:
        """

        :return: the (raw) key to press or None if the simulation finished
        """
        if self.__notification_popup:
            # close the notification popup if it is still open before using any real simulation keys
            self.__notification_popup = False
            return self.__controls.get_key(Keys.PopupClose)
        while self.__cur_chunk is not None:
            key = self.__next_key()
            if key > -1:
                return key
        self.__finished = True
        return None

    def to_string(self, skip_header: bool = False, skip_raw_keys: bool = False, skip_logical_keys: bool = False) -> str:
        str_repr = ""
        if not skip_header:
            str_repr += self.__version + "\n"
            str_repr += str(self.__seed) + "\n"
            str_repr += str(self.__time) + "\n"
            str_repr += GameplayConfig.to_file_text() + "\n"

        if skip_raw_keys and skip_logical_keys:
            return str_repr

        if not skip_header: str_repr += "\n\nKeys:"     # add keys header

        key_strings = []
        while True:
            k = self.next()
            if k is None: break

            if skip_raw_keys:
                key_strings.append(Keys(self.__controls.encode(k)).name)
            elif skip_logical_keys:
                key_strings.append(str(k))
            else:
                key_strings.append(f"{k} ({Keys(self.__controls.encode(k)).name})")

        str_repr += "\n".join(key_strings) + "\n"
        return str_repr

    def version_warning(self) -> Tuple[str, str]:
        __space = "Space"
        return "Starting Simulation", \
               f"You started a run with \nseed = {self.seed}\nrecorded at {self.time}.\n" \
               f"Press {ColorConfig.highlight_key(__space)} to execute the simulation step by step. " \
               f"Alternatively, if you keep it pressed the simulation will be executed automatically with short " \
               f"delays after each step until you let go of Space again."

    def version_alright(self) -> Tuple[str, str]:
        return "Simulating other version", \
               "You try to simulate the run of a different game version.\n" \
               f"Your current version: {Config.version()}\n" \
               f"Version you try to simulate: {self.version}\n" \
               "This is not supported and can cause problems. Only continue if you know what you do! Else close this " \
               "popup and press ESC to abort the simulation."

    def stop_message(self) -> str:
        if self.__finished:
            text = "finished Simulation"
        else:
            text = "stopped Simulator"
        text += f"\n{Logger.instance().error_count} errors occurred while simulating"
        return text
