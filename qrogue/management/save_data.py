
from qrogue.game.logic.actors import Player, Robot
from qrogue.game.logic.actors.controllables import TestBot, LukeBot
from qrogue.game.world.map import CallbackPack
from qrogue.util import Logger, PathConfig, AchievementManager


class SaveData:
    __NUMBER_OF_SAVE_FILES = 7    # how many save files can be present before we delete the oldest one  # todo maybe move to Config?
    __instance = None
    SAVE_NAME = "qrogue-save"

    @staticmethod
    def instance() -> "SaveData":
        if SaveData.__instance is None:
            Logger.instance().throw(Exception("This singleton has not been initialized yet!"))
        return SaveData.__instance

    def __init__(self):
        if SaveData.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            self.__achievements = AchievementManager()
            self.__player = Player()
            #path = PathConfig.find_latest_save_file()
            #content = ""
            #try:
            #    content = PathConfig.read(path, True)
            #except FileNotFoundError:
            #    Logger.instance().error(NotImplementedError("This line should not be reachable! Please send us the log "
            #                                                "files so we can fix the issue as soon as possible. Thank you!"))
            # todo parse content
            self.__expeditions_finished = 0
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
        return 7    # todo implement

    def available_robots(self) -> iter:
        return iter(self.__available_robots)

    def get_robot(self, index: int) -> Robot:
        if 0 <= index < len(self.__available_robots):
            return self.__available_robots[index]
        return None

    def save(self):
        data = ""
        PathConfig.new_save_file(data)
