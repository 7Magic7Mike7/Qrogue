import os
from datetime import datetime

from qrogue.util.config import CheatConfig, GameplayConfig, PathConfig, TestConfig


class Config:   # todo make singleton and handle access to other configs?
    __frame_count = 0
    MAX_SEED = 1000000
    __VERSION = "v0.6.1"
    __GAME_CONFIG = "qrogue_game.config"
    __GAMEPLAY_HEAD = "[Gameplay]\n"
    __DEBUG = False
    __TEST_LEVEL = False

    __HEADER = "Qrogue "
    __SEED_HEAD = "Seed="
    __TIME_HEAD = "Time="
    __CONFIG_HEAD = "[Config]"

    @staticmethod
    def HEADER() -> str:
        return Config.__HEADER

    @staticmethod
    def SEED_HEAD() -> str:
        return Config.__SEED_HEAD

    @staticmethod
    def TIME_HEAD() -> str:
        return Config.__TIME_HEAD

    @staticmethod
    def CONFIG_HEAD() -> str:
        return Config.__CONFIG_HEAD

    @staticmethod
    def examiner_name() -> str:
        return "Examiner"   # for things the scientist says during the exam

    @staticmethod
    def scientist_name() -> str:
        return "Robb"

    @staticmethod
    def system_name() -> str:
        return "System"     # for things the robot's system tells us

    @staticmethod
    def player_name() -> str:
        return "Mike"

    @staticmethod
    def get_name(value: int) -> str:
        if value == 0:
            return Config.examiner_name()
        if value == 1:
            return Config.scientist_name()
        if value == 2:
            return Config.system_name()
        if value == 3:
            return Config.player_name()

        return Config.system_name()     # default if nothing valid was specified

    @staticmethod
    def version() -> str:
        return Config.__VERSION

    @staticmethod
    def get_log_head(seed: int) -> str:
        now_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        head = f"{Config.__HEADER}{Config.version()}\n"
        head += f"{Config.__SEED_HEAD}{seed}\n"
        head += f"{Config.__TIME_HEAD}{now_str}\n\n"
        head += f"{Config.__CONFIG_HEAD}\n{GameplayConfig.to_file_text()}\n"
        return head

    @staticmethod
    def game_config_file() -> str:
        return Config.__GAME_CONFIG

    @staticmethod
    def forbid_saving() -> bool:
        if Config.debugging():
            # in debugging saving is never forbidden
            return False
        return CheatConfig.did_cheat()

    @staticmethod
    def debugging() -> bool:
        return Config.__DEBUG

    @staticmethod
    def test_level(ignore_debugging: bool = False) -> bool:
        return Config.__TEST_LEVEL and (Config.debugging() or ignore_debugging)

    @staticmethod
    def debug_print(text: str):
        if Config.debugging():
            print(text)

    @staticmethod
    def activate_debugging(test_level: bool = False):
        Config.__DEBUG = True
        Config.__TEST_LEVEL = test_level

    @staticmethod
    def setup_user_data(custom_path: str = None):
        """
        Sets up the folder structure and default game config in the specified path.
        :param custom_path: where to store and load the user data (e.g. logs, save data)
        :return:
        """

        if custom_path:
            user_data_path = custom_path
        else:
            user_data_path = PathConfig.user_data_path()

        PathConfig.create_folder_structure(user_data_path)
        path = os.path.join(user_data_path, Config.__GAME_CONFIG)
        if not os.path.exists(path):
            text = ""
            text += Config.__GAMEPLAY_HEAD
            text += GameplayConfig.to_file_text()
            with open(path, "x") as file:
                file.write(text)

    @staticmethod
    def load():
        if not os.path.exists(PathConfig.user_data_path(Config.__GAME_CONFIG)):
            Config.setup_user_data()

        if not Config.load_gameplay_config():
            return 2

        return 0

    @staticmethod
    def load_gameplay_config() -> bool:
        try:
            content = PathConfig.read(Config.game_config_file(), in_user_path=True)
            gameplay_start = content.index(Config.__GAMEPLAY_HEAD) + len(Config.__GAMEPLAY_HEAD)
            if GameplayConfig.from_log_text(content[gameplay_start:len(content)]):
                return True
        except FileNotFoundError:
            raise FileNotFoundError("Could not load the game's config file!")
        return False

    @staticmethod
    def save_gameplay_config() -> bool:
        text = f"{Config.__GAMEPLAY_HEAD}\n{GameplayConfig.to_file_text()}\n"
        PathConfig.write(Config.game_config_file(), text, in_user_path=True, may_exist=True, append=False)
        return True

    @staticmethod
    def skip_persisting() -> bool:
        return TestConfig.is_active()

    @staticmethod
    def inc_frame_count():
        Config.__frame_count += 1

    @staticmethod
    def frame_count() -> int:
        return Config.__frame_count

    @staticmethod
    def loading_refresh_time() -> float:
        return 0.2  # in seconds
