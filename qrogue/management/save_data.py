
from qrogue.game.logic.actors import Player, Robot
from qrogue.game.logic.actors.controllables import TestBot, LukeBot
from qrogue.game.world.map import CallbackPack
from qrogue.util import Logger, PathConfig, AchievementManager, RandomManager
from qrogue.util.achievements import Achievement


class SaveData:
    __ROBOT_SECTION = "[Robots]"
    __COLLECTIBLE_SECTION = "[Collectibles]"
    __ACHIEVEMENT_SECTION = "[Achievements]"
    __instance = None

    @staticmethod
    def instance() -> "SaveData":
        if SaveData.__instance is None:
            Logger.instance().throw(Exception("This singleton has not been initialized yet!"))
        return SaveData.__instance

    @staticmethod
    def __empty_save_file() -> str:
        pass

    def __init__(self):
        if SaveData.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            self.__player = Player()
            path = PathConfig.find_latest_save_file()
            content = ""
            try:
                content = PathConfig.read(path, in_user_path=True).splitlines()
            except FileNotFoundError:
                Logger.instance().error(NotImplementedError("This line should not be reachable! Please send us the log "
                                                            "files so we can fix the issue as soon as possible. "
                                                            "Thank you!"))
            index = content.index(SaveData.__ACHIEVEMENT_SECTION)
            achievement_list = []
            for i in range(index + 1, len(content)):
                achievement = Achievement.from_string(content[i])
                if achievement:
                    achievement_list.append(achievement)
            self.__achievements = AchievementManager(achievement_list)

            self.__available_robots = [
                TestBot(CallbackPack.instance().game_over),
                LukeBot(CallbackPack.instance().game_over),
            ]
            SaveData.__instance = self

    @property
    def achievement_manager(self) -> AchievementManager:
        return self.__achievements

    @property
    def player(self) -> Player:
        return self.__player

    def get_expedition_seed(self) -> int:
        return RandomManager.instance().get_seed()  #7    # todo implement

    def available_robots(self) -> iter:
        return iter(self.__available_robots)

    def get_robot(self, index: int) -> Robot:
        if 0 <= index < len(self.__available_robots):
            return self.__available_robots[index]
        return None

    def save(self) -> bool:
        data = ""
        data += f"{SaveData.__ROBOT_SECTION}\n"
        data += f"{SaveData.__COLLECTIBLE_SECTION}\n"
        data += f"{SaveData.__ACHIEVEMENT_SECTION}\n"
        data += f"{self.achievement_manager.to_string()}\n"
        PathConfig.new_save_file(data)
        return True
