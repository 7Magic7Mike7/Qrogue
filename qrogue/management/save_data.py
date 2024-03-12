import os.path
from typing import Tuple, Optional, List

from qrogue.game.logic.actors import Player, Robot
from qrogue.game.logic.actors.controllables import BaseBot, LukeBot
from qrogue.game.world.map import CallbackPack
from qrogue.util import Logger, PathConfig, FileTypes, AchievementManager, RandomManager, CommonPopups, Config, \
    TestConfig, ErrorConfig, achievements
from qrogue.util.achievements import Achievement, Unlocks, AchievementType


class SaveData:
    __ROBOT_SECTION = "[Robots]"
    __COLLECTIBLE_SECTION = "[Collectibles]"
    __ACHIEVEMENT_SECTION = "[Achievements]"
    __instance = None

    __FRESH_START_ACHIEVEMENTS: List[Achievement] = [
        Achievement(achievements.CompletedExpedition, AchievementType.Expedition, 0, 100),
        # worlds
        Achievement("w0", AchievementType.World, 0, 7),
        # auto unlocks (i.e., was previously unlocked in a certain way but now unlocked from the very beginning)
        Achievement.from_unlock(Unlocks.GateRemove),
    ]

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

            # add the fresh start achievements or else load everything from the file
            achievement_list = SaveData.__FRESH_START_ACHIEVEMENTS.copy() if self.__is_fresh_save else []
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

    def achievement_iterator(self) -> Iterator[Achievement]:
        return self.achievement_manager.achievement_iterator()

    def restart_level_timer(self):
        return self.achievement_manager.restart_level_timer()

    def check_unlocks(self, unlocks: Union[str, Unlocks]) -> bool:
        if isinstance(unlocks, str): unlocks = Unlocks.from_name(unlocks)
        return self.achievement_manager.check_unlocks(unlocks)

    def check_achievement(self, name: str) -> bool:
        return self.achievement_manager.check_achievement(name)

    def reset_level_events(self):
        self.achievement_manager.reset_level_events()

    def add_to_achievement(self, name: str, score: float = 1):
        return self.achievement_manager.add_to_achievement(name, score)

    def trigger_global_event(self, name: str, score: float = 1):
        return self.achievement_manager.trigger_global_event(name, score)

    def trigger_event(self, name: str, score: float = 1):
        return self.achievement_manager.trigger_event(name, score)

    def finished_level(self, internal_name: str, display_name: str = None) -> bool:
        return self.achievement_manager.finished_level(internal_name, display_name)

    def to_string(self) -> str:
        data = ""
        data += f"{SaveData.__ROBOT_SECTION}\n"
        data += f"{SaveData.__COLLECTIBLE_SECTION}\n"
        data += f"{SaveData.__ACHIEVEMENT_SECTION}\n"
        data += f"{self.achievement_manager.to_string()}\n"
        return data

    def save(self, is_auto_save: bool = False) -> Tuple[bool, CommonPopups]:
        if Config.forbid_saving():
            return False, CommonPopups.NoSavingWithCheats
        try:
            data = ""
            data += f"{SaveData.__ROBOT_SECTION}\n"
            data += f"{SaveData.__COLLECTIBLE_SECTION}\n"
            data += f"{SaveData.__ACHIEVEMENT_SECTION}\n"
            data += f"{self.achievement_manager.to_string()}\n"
            if is_auto_save:
                PathConfig.write_auto_save(data)
            else:
                PathConfig.new_save_file(data)
            return True, CommonPopups.SavingSuccessful
        except:
            return False, CommonPopups.SavingFailed
