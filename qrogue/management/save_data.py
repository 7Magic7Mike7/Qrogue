import os.path
from typing import Tuple, Optional

from qrogue.game.logic.actors import Player, Robot
from qrogue.game.logic.actors.controllables import BaseBot, LukeBot
from qrogue.game.world.map import CallbackPack
from qrogue.util import Logger, PathConfig, FileTypes, AchievementManager, RandomManager, CommonPopups, Config, \
    TestConfig, ErrorConfig
from qrogue.util.achievements import Achievement


class SaveData:
    __ROBOT_SECTION = "[Robots]"
    __COLLECTIBLE_SECTION = "[Collectibles]"
    __ACHIEVEMENT_SECTION = "[Achievements]"
    __instance = None

    @staticmethod
    def instance() -> "SaveData":
        if SaveData.__instance is None:
            Logger.instance().throw(Exception(ErrorConfig.singleton_no_init("SaveData")))
        return SaveData.__instance

    @staticmethod
    def reset():
        if TestConfig.is_active():
            SaveData.__instance = None
        else:
            raise TestConfig.StateException(ErrorConfig.singleton_reset("SaveData"))

    def __init__(self):
        if SaveData.__instance is not None:
            Logger.instance().throw(Exception(ErrorConfig.singleton("SaveData")))
        else:
            self.__player = Player()
            path = PathConfig.find_latest_save_file()
            # a fresh save has no digit before the file ending
            self.__is_fresh_save = not path[-len(FileTypes.Save.value)-1].isdigit()
            content = ""
            try:
                content = PathConfig.read(path, in_user_path=True).splitlines()
            except FileNotFoundError:
                Logger.instance().throw(NotImplementedError("This line should not be reachable! Please send us the log "
                                                            "files so we can fix the issue as soon as possible. "
                                                            "Thank you!"))
            index = content.index(SaveData.__ACHIEVEMENT_SECTION)
            achievement_list = []
            for i in range(index + 1, len(content)):
                achievement = Achievement.from_string(content[i])
                if achievement:
                    achievement_list.append(achievement)
            AchievementManager(achievement_list)

            self.__available_robots = [
                BaseBot(CallbackPack.instance().game_over),
                LukeBot(CallbackPack.instance().game_over),
            ]
            SaveData.__instance = self

    @property
    def achievement_manager(self) -> AchievementManager:
        return AchievementManager.instance()

    @property
    def player(self) -> Player:
        return self.__player

    @property
    def story_progress(self) -> int:
        return self.achievement_manager.story_progress

    @property
    def is_fresh_save(self) -> bool:
        return self.__is_fresh_save

    def get_expedition_seed(self) -> int:
        return RandomManager.instance().get_seed(msg="SaveData.get_expedition_seed()")  #7    # todo implement

    def available_robots(self) -> iter:
        return iter(self.__available_robots)

    def get_robot(self, index: int) -> Optional[Robot]:
        if 0 <= index < len(self.__available_robots):
            return self.__available_robots[index]
        return None

    def save(self) -> Tuple[bool, CommonPopups]:
        if Config.forbid_saving():
            return False, CommonPopups.NoSavingWithCheats
        try:
            data = ""
            data += f"{SaveData.__ROBOT_SECTION}\n"
            data += f"{SaveData.__COLLECTIBLE_SECTION}\n"
            data += f"{SaveData.__ACHIEVEMENT_SECTION}\n"
            data += f"{self.achievement_manager.to_string()}\n"
            PathConfig.new_save_file(data)
            return True, CommonPopups.SavingSuccessful
        except:
            return False, CommonPopups.SavingFailed
