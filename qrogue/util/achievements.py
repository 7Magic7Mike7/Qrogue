import datetime
import enum
from typing import List, Dict, Iterator, Optional

from qrogue.util import MapConfig, ErrorConfig, Logger, GameplayConfig
from qrogue.util.util_functions import cur_datetime, time_diff

# global events
#FinishedTutorial = "CompletedTutorial"
#EnteredPauseMenu = "EnteredPauseMenu"
CompletedExpedition = "CompletedExpedition"
#EnteredNavigationPanel = "EnteredNavigationPanel"


class Unlocks(enum.Enum):
    # menu unlocks
    MainMenuContinue = (10, "MainMenuContinue")     # unlocked after Level 0
    MainMenuPlay = (11, "MainMenuPlay")             # unlocked after first "real" level (i.e., after spaceship)

    # hud unlocks
    ShowEnergy = (30, "ShowEnergy")     # unlocked after Level 0

    # puzzle unlocks
    ShowEquation = (55, "ShowEquation")   # whether to show the matrix vector multiplication above the circuit
    GateRemove = (52, "GateRemove")     # unlocked automatically
    CircuitReset = (50, "CircuitReset")     # unlocked after Tutorial
    PuzzleFlee = (51, "PuzzleFlee")     # unlocked in Level 1

    # level unlocks
    ProceedChoice = (90, "ProceedChoice")   # unlocked after all Tutorial levels (right before Exam)    # todo: should be available as soon as Level Selection is available

    # spaceship unlocks
    Spaceship = (100, "Spaceship")      # unlocked after Tutorial
    Workbench = (110, "Workbench")      # unlocking not yet implemented
    Navigation = (130, "Navigation")    # unlocked after Tutorial
    FreeNavigation = (131, "FreeNavigation")    # unlocked never
    QuickStart = (140, "QuickStart")    # unlocking not yet implemented

    def __init__(self, id_: int, name: str):
        self.__id = id_
        self.__name = name

    @property
    def id(self) -> int:
        return self.__id

    @property
    def ach_name(self) -> str:
        return self.__name.lower()

    @staticmethod
    def in_map_reference() -> str:
        return "unlocks"

    @staticmethod
    def from_name(name: str) -> Optional["Unlocks"]:
        name = name.lower()     # normalize name
        for unlock in Unlocks:
            if unlock.name.lower() == name:
                return unlock
        return None


class Ach:
    __LEVEL_COMPLETION_UNLOCKS: Dict[str, List[Unlocks]] = {
        # newbie tutorials
        "l0k0v0": [Unlocks.MainMenuContinue, Unlocks.ShowEnergy, ],
        "l0k0v1": [Unlocks.ShowEquation],

        # experienced tutorials
        "l0k1v0": [Unlocks.MainMenuContinue, Unlocks.ShowEnergy, ],
        "l0k1v1": [Unlocks.ShowEquation],

        # other levels
    }

    @staticmethod
    def get_level_completion_unlocks(level_name: str) -> List[Unlocks]:
        if level_name in Ach.__LEVEL_COMPLETION_UNLOCKS:
            return Ach.__LEVEL_COMPLETION_UNLOCKS[level_name]
        return []


class Achievement:
    __DATA_SEPARATOR = ">q<"

    @staticmethod
    def from_string(text: str) -> "Achievement":
        data = text.split(Achievement.__DATA_SEPARATOR)
        if len(data) == 5:
            name = data[0]
            #atype = AchievementType(int(data[1]))
            score = float(data[2])
            done_score = float(data[3])
            return Achievement(name, score, done_score)

    #@staticmethod
    #def from_unlock(unlock: Unlocks) -> "Achievement":
    #    return Achievement(unlock.ach_name, AchievementType.Unlock, 1, 1)

    def __init__(self, name: str, score: float, done_score: float,
                 date_time: Optional[datetime.datetime] = None):
        self.__name = name
        self.__score = score
        self.__done_score = done_score
        # date_time is either the datetime of the last scoring of the achievement or the datetime of completing the
        # achievement (score >= done_score)
        self.__date_time = datetime.datetime.now() if date_time is None else date_time

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> int: #AchievementType:
        raise Exception("Should no longer be used!")

    @property
    def score(self) -> float:
        return self.__score

    @property
    def done_score(self) -> float:
        return self.__done_score

    @property
    def date_time(self) -> datetime.datetime:
        return self.__date_time

    def is_done(self) -> bool:
        return self.score >= self.done_score

    def add_score(self, score: float) -> bool:  # todo change name to increase_score and make score default to 1?
        """

        :param score: how much score points we want to add
        :return: True if we changed the score, False otherwise
        """
        if score > 0 and not self.is_done():
            # update our scoring timestamp - if this call completed the achievement, date_time will never be udpated
            # again, making date_time the datetime of completion
            self.__date_time = datetime.datetime.now()
            self.__score = min(self.score + score, self.done_score)
            return True
        return False

    def to_string(self) -> str:
        text = f"{self.name}{Achievement.__DATA_SEPARATOR}"
        #text += f"{self.type.value}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.score}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.done_score}{Achievement.__DATA_SEPARATOR}"
        return text

    def to_display_string(self) -> str:
        if self.is_done():
            text = "[X]"
        else:
            text = "[_]"
        #if self.type is AchievementType.Secret:
        #    text += "???"
        #else:
        text += f" {self.name} ({self.score} / {self.done_score})"
        return text

    def __str__(self) -> str:
        return self.to_string()


# todo: is no longer used, but I don't delete it yet since I might re-use some code parts for cleaner
#  achievement-handling in NewSaveData
class AchievementManager:
    __DISPLAY_STRING_INDENT = "  "
    __instance = None

    @staticmethod
    def instance() -> "AchievementManager":
        if AchievementManager.__instance is None:
            Logger.instance().throw(Exception(ErrorConfig.singleton_no_init("AchievementManager")))
        return AchievementManager.__instance

    def __init__(self, achievements: List[Achievement]):
        if False:   #AchievementManager.__instance is not None:
            Logger.instance().throw(Exception(ErrorConfig.singleton("AchievementManager")))
        else:
            self.__storage: Dict[str, Achievement] = {}
            self.__temp_level_storage: Dict[str, Achievement] = {}
            self.__level_start_timestamp = cur_datetime()


            # todo use more dynamic "difficulty" system after user study?
            newbie_mode_counter = 0
            expert_mode_counter = 0

            #story_counter = 0
            #for achievement in achievements:
                #if achievement.type is not AchievementType.Implicit:
                    #if achievement.type is AchievementType.Story and achievement.is_done():
                    #    story_counter += 1
                    #self.__storage[achievement.name] = achievement
                    #if achievement.name.startswith("l0k"):
                    #    if achievement.name.startswith("l0k0"): newbie_mode_counter += 1
                    #    elif achievement.name.startswith("l0k1"): expert_mode_counter += 1

            if expert_mode_counter > newbie_mode_counter:
                GameplayConfig.set_experienced_mode()
            else:
                GameplayConfig.set_newbie_mode()

            #self.__storage["Story"] = Achievement("Story", AchievementType.Implicit, story_counter, 100)

    def _store_achievement(self, achievement: Achievement):
        if int(achievement.score) != 1:
            raise Exception("Is this happening?")

        if achievement.name in self.__storage:
            self.__storage[achievement.name].add_score(achievement.score)
        else:
            self.__storage[achievement.name] = achievement

    def check_achievement(self, name: str) -> bool:
        if name in self.__temp_level_storage:
            achievement = self.__temp_level_storage[name]
            return achievement.is_done()
        elif name in self.__storage:
            achievement = self.__storage[name]
            return achievement.is_done()
        elif name.startswith(Unlocks.in_map_reference()):   # so we can check for unlocks in levels and worlds if needed
            Logger.instance().error(f"Tried to check the Unlock \"{name}\" with check_achievement()!")
            return False
        return False

    def check_unlocks(self, unlocks: Unlocks) -> bool:
        return self.check_achievement(unlocks.ach_name)

    def reset_level_events(self):
        self.__temp_level_storage.clear()

    def add_to_achievement(self, name: str, score: float = 1):
        if name in self.__storage:
            self.__storage[name].add_score(score)

    def trigger_event(self, name: str, score: float = 1):
        """
        Triggers an event (either global or local/level-wise) by creating or adding to the corresponding achievement.

        :param name: name of the event (needs to be unique)
        :param score: by how much the event should progress (only relevant if it can be triggered multiple times from
                        different sources
        """
        # todo: is no longer in use
        if name.startswith(MapConfig.global_event_prefix()):
            name = name[len(MapConfig.global_event_prefix()):]  # remove prefix
            #self.trigger_global_event(name)

        elif name.startswith(MapConfig.unlock_prefix()):
            name = name[len(MapConfig.unlock_prefix()):]    # remove prefix
            #self._store_achievement(Achievement(name, AchievementType.Unlock, score, score))

        else:
            if name in self.__temp_level_storage:
                self.__temp_level_storage[name].add_score(score)
            #else:
                #self.__temp_level_storage[name] = Achievement(name, AchievementType.Event, score, score)

    def finished_level(self, level: str, display_name: str = None) -> bool:
        level_end_time_stamp = cur_datetime()
        level_duration, _ = time_diff(self.__level_start_timestamp, level_end_time_stamp)
        Logger.instance().info(f"Finished level {level} after {level_duration}s.", from_pycui=False)

        #for unlock in Ach.get_level_completion_unlocks(level):
        #    self._store_achievement(Achievement.from_unlock(unlock))

        if level in self.__storage and self.__storage[level].is_done():
            return False
        else:
            #self.__storage[level] = Achievement(level, AchievementType.Level, 1, 1)
            #self.__on_achievement_completion(self.__storage[level])
            return True

    def to_string(self) -> str:
        text = ""
        for value in self.__storage.values():
            #if value.type is AchievementType.Implicit:
            #    continue
            text += f"{value.to_string()}\n"
        return text

    def to_display_string(self) -> str:
        #type_text = {}
        #for value in self.__storage.values():
        #    if value.type in type_text:
        #        type_text[value.type].append(value.to_display_string())
        #    else:
        #        type_text[value.type] = [value.to_display_string()]

        text = ""
        # first add the temporary level events
        if len(self.__temp_level_storage) > 0:
            #text += f"{AchievementType.Event.name}\n"
            for event in self.__temp_level_storage.values():
                text += f"{AchievementManager.__DISPLAY_STRING_INDENT}{event.to_display_string()}\n"
        # now add permanent the achievements
        #for a_type in AchievementType.get_display_order():
        #    if a_type in type_text:
        #        text += f"{a_type.name}\n"
        #        for achievement in type_text[a_type]:
        #            text += f"{AchievementManager.__DISPLAY_STRING_INDENT}{achievement}\n"
        return text

    def __str__(self) -> str:
        return self.to_string()
