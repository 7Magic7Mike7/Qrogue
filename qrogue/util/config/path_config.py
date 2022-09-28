import enum
import os
import pathlib
from datetime import datetime
from typing import Tuple


class FileTypes(enum.Enum):
    Log = ".qrlog"
    KeyLog = ".qrkl"
    ScreenPrint = ".qrsc"
    Save = ".qrsave"
    Dungeon = ".qrdg"
    World = ".qrw"
    Templates = ".txt"


class PathConfig:
    __DATA_FOLDER = "data"
    __DEFAULT_GAME_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", __DATA_FOLDER)
    __DEFAULT_USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "QrogueData")
    __LOG_FOLDER = "logs"
    __KEY_LOG_FOLDER = "keylogs"
    __SCREEN_PRINTS_FOLDER = "screenprints"
    __SAVE_DATA_FOLDER = "saves"
    __DUNGEON_FOLDER = "dungeons"
    __TEMPLATE_ROOMS = "rooms"
    __TEMPLATE_HALLWAYS = "hallways"
    __TEMPLATE_STV_POOLS = "stv_pools"
    __TEMPLATE_REWARD_POOLS = "reward_pools"
    __TEMPLATE_FILE = f"templates{FileTypes.Templates.value}"
    __SAVE_FILE_PREFIX = "qrogue-save"
    __FRESH_SAVE_FILE = "fresh"
    __SAVE_FILE_NUMERATION_SEPARATOR = "_"
    __NUMBER_OF_SAVE_FILES = 7    # how many save files can be present before we delete the oldest one

    __Base_Path = __DEFAULT_GAME_DATA_PATH
    __User_Data_Path = __DEFAULT_USER_DATA_PATH

    @staticmethod
    def __now_str() -> str:
        return datetime.now().strftime("%d%m%Y_%H%M%S")

    @staticmethod
    def __save_file_str(num: int) -> str:
        return os.path.join(PathConfig.__SAVE_DATA_FOLDER,
                            f"{PathConfig.__SAVE_FILE_PREFIX}{PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR}{num}"
                            f"{FileTypes.Save.value}")

    @staticmethod
    def __get_save_files_stats() -> Tuple[int, int]:
        """

        :return: number of available save files, number of the latest save file
        """
        files = os.listdir(PathConfig.user_data_path(PathConfig.__SAVE_DATA_FOLDER))
        num = -1
        num_of_files = 0
        for file in files:
            if file.startswith(PathConfig.__SAVE_FILE_PREFIX) and file.endswith(FileTypes.Save.value):
                file_ending_index = len(file) - len(FileTypes.Save.value)
                num_of_files += 1
                cur_num = int(file[file.rindex(PathConfig.__SAVE_FILE_NUMERATION_SEPARATOR) + 1:file_ending_index])
                if cur_num > num:
                    num = cur_num
        return num_of_files, num

    @staticmethod
    def launch_config_path() -> str:
        return os.path.join(PathConfig.__Base_Path, "qrogue_launch.config")

    @staticmethod
    def default_base_path() -> str:
        return PathConfig.__DEFAULT_GAME_DATA_PATH

    @staticmethod
    def default_user_data_path() -> str:
        return PathConfig.__DEFAULT_USER_DATA_PATH

    @staticmethod
    def keylog_folder() -> str:
        return PathConfig.__KEY_LOG_FOLDER

    @staticmethod
    def create_folder_structure(user_data_path: str) -> None:
        pathlib.Path(user_data_path).mkdir(parents=True, exist_ok=True)
        log_path = os.path.join(user_data_path, PathConfig.__LOG_FOLDER)
        key_log_path = os.path.join(user_data_path, PathConfig.__KEY_LOG_FOLDER)
        screen_prints_path = os.path.join(user_data_path, PathConfig.__SCREEN_PRINTS_FOLDER)
        save_data_path = os.path.join(user_data_path, PathConfig.__SAVE_DATA_FOLDER)

        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(key_log_path):
            os.mkdir(key_log_path)
        if not os.path.exists(screen_prints_path):
            os.mkdir(screen_prints_path)
        if not os.path.exists(save_data_path):
            os.mkdir(save_data_path)

    @staticmethod
    def set_base_path(base_path: str):
        if os.path.exists(base_path):
            PathConfig.__Base_Path = base_path
        else:
            raise FileNotFoundError(f"Given base path is not valid: {base_path} [normalized value = "
                                    f"{os.path.normpath(base_path)}]")

    @staticmethod
    def set_user_data_path(user_data_path: str):
        PathConfig.create_folder_structure(user_data_path)  # does nothing for existing folders
        PathConfig.__User_Data_Path = user_data_path

    @staticmethod
    def load_paths(custom_data_path: str, custom_user_data_path: str) -> bool:
        try:
            if custom_data_path is None or custom_user_data_path is None:
                with open(PathConfig.launch_config_path()) as f:
                    content = f.readlines()

            if custom_data_path:
                data_path = custom_data_path
            else:
                data_path = content[1]
            if custom_user_data_path:
                user_data_path = custom_user_data_path
            else:
                user_data_path = content[2]

            if data_path == "\n":
                data_path = PathConfig.default_base_path()
            elif data_path.endswith("\n"):
                data_path = data_path[:-1]
            if user_data_path == "\n":
                user_data_path = PathConfig.default_user_data_path()
            elif user_data_path.endswith("\n"):
                user_data_path = user_data_path[:-1]

            PathConfig.set_base_path(data_path)
            PathConfig.set_user_data_path(user_data_path)
            return os.path.exists(PathConfig.__Base_Path) and os.path.exists(PathConfig.__User_Data_Path)
        except Exception as error:
            print(error)
            return False

    @staticmethod
    def base_path(file_name: str = "") -> str:
        return os.path.join(PathConfig.__Base_Path, file_name)

    @staticmethod
    def user_data_path(file_name: str = "") -> str:
        return os.path.join(PathConfig.__User_Data_Path, file_name)

    @staticmethod
    def new_log_file(seed: int) -> str:
        now_str = PathConfig.__now_str()
        return os.path.join(PathConfig.__LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.Log.value}")

    @staticmethod
    def new_key_log_file(seed: int, is_level: bool = True) -> str:
        now_str = PathConfig.__now_str()
        if is_level:
            return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}_seed{seed}{FileTypes.KeyLog.value}")
        else:
            return os.path.join(PathConfig.__KEY_LOG_FOLDER, f"{now_str}_meta{seed}{FileTypes.KeyLog.value}")

    @staticmethod
    def new_screen_print(text: str):
        now_str = PathConfig.__now_str()
        path = os.path.join(PathConfig.__SCREEN_PRINTS_FOLDER, f"{now_str}{FileTypes.ScreenPrint.value}")
        PathConfig.write(path, now_str + "\n" + text, may_exist=True, append=True)

    @staticmethod
    def new_save_file(text: str):
        now_str = PathConfig.__now_str()
        num_of_files, num = PathConfig.__get_save_files_stats()

        # increment to get the highest number for the new save file (if no save file exists yet, -1 will be incremented
        # to 0)
        num += 1
        if num_of_files >= PathConfig.__NUMBER_OF_SAVE_FILES:
            oldest_num = num - PathConfig.__NUMBER_OF_SAVE_FILES
            PathConfig.delete(PathConfig.__save_file_str(oldest_num))
        PathConfig.write(PathConfig.__save_file_str(num), now_str + "\n" + text, may_exist=False)

    @staticmethod
    def find_latest_save_file() -> str:
        _, num = PathConfig.__get_save_files_stats()
        if num >= 0:
            return PathConfig.__save_file_str(num)
        else:
            return PathConfig.base_path(f"{PathConfig.__FRESH_SAVE_FILE}{FileTypes.Save.value}")

    @staticmethod
    def read_keylog_buffered(file_name: str, in_keylog_folder: bool = True, buffer_size: int = 1024) -> str:
        if not file_name.endswith(FileTypes.KeyLog.value):
            file_name += FileTypes.KeyLog.value
        if in_keylog_folder:
            path = PathConfig.user_data_path(os.path.join(PathConfig.__KEY_LOG_FOLDER, file_name))
        else:
            path = file_name
        if os.path.exists(path):
            with open(path, "r") as file:
                data = file.read(buffer_size)
                while data:
                    yield data
                    data = file.read(buffer_size)
        else:
            raise FileNotFoundError(f"There is no such key log file: {path}")

    @staticmethod
    def read_world(file_name: str, in_dungeon_folder: bool = True):
        if not file_name.endswith(FileTypes.World.value):
            file_name += FileTypes.World.value

        if in_dungeon_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__DUNGEON_FOLDER, file_name))
        else:
            path = file_name
        return PathConfig.read(path, in_user_path=False)

    @staticmethod
    def read_level(file_name: str, in_dungeon_folder: bool = True):
        if not file_name.endswith(FileTypes.Dungeon.value):
            file_name += FileTypes.Dungeon.value

        if in_dungeon_folder:
            path = PathConfig.base_path(os.path.join(PathConfig.__DUNGEON_FOLDER, file_name))
        else:
            path = file_name
        return PathConfig.read(path, in_user_path=False)

    @staticmethod
    def read(file_name: str, in_user_path: bool) -> str:
        if in_user_path:
            path = PathConfig.user_data_path(file_name)
        else:
            path = file_name
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
            return content
        else:
            raise FileNotFoundError(f"File \"{file_name}\" could not be found!")

    @staticmethod
    def write(path: str, text: str, in_user_path: bool = True, may_exist: bool = True, append: bool = False):
        if in_user_path:
            path = PathConfig.user_data_path(path)  # data in base_path is static so we can only write user data
        mode = "x"
        if may_exist:
            if os.path.exists(path):
                mode = "w"
                if append:
                    mode = "a"
        with open(path, mode) as file:
            file.write(text)

    @staticmethod
    def delete(file_name):
        path = PathConfig.user_data_path(file_name)     # data in base_path is static so we can only delete user data
        if os.path.exists(path):
            os.remove(path)
