import enum
from typing import List

from qrogue.util import MapConfig

FinishedTutorial = "CompletedTutorial"
EnteredPauseMenu = "EnteredPauseMenu"
FirstDoorUnlocked = "UnlockedDoor"
CompletedExpedition = "CompletedExpedition"
UnlockedWorkbench = "UnlockedWorkbench"


class Unlocks(enum.Enum):
    # global unlocks
    Saving = 0

    # menu unlocks
    MainMenuContinue = 10
    MainMenuPlay = 11

    # hud unlocks
    ShowEnergy = 30

    # puzzle unlocks
    CircuitReset = 50
    PuzzleFlee = 51

    # level unlocks
    ProceedChoice = 90

    # spaceship unlocks
    Spaceship = 100
    Navigation = 130
    FreeNavigation = 131

    @staticmethod
    def in_map_reference() -> str:
        return "unlocks"


class Ach:
    __EXAM_DONE_PROGRESS = 8

    @staticmethod
    def story() -> str:
        return "Story"

    @staticmethod
    def is_story_mission(level_name: str) -> bool:
        # check if level_name is from one of the tutorial lessons
        if level_name.startswith(MapConfig.tutorial_lesson_prefix()) and \
                0 <= int(level_name[len(MapConfig.tutorial_lesson_prefix()):]) < MapConfig.num_of_lessons():
            return True
        return level_name in [
            MapConfig.exam(),
        ]

    @staticmethod
    def check_unlocks(unlock: Unlocks, progress: int) -> bool:
        if unlock is Unlocks.Saving:
            # there is something we can save
            return progress > 0

        elif unlock is Unlocks.MainMenuContinue:
            # something was already completed so continue is no longer the same than a fresh start
            return progress > 0
        elif unlock is Unlocks.MainMenuPlay:
            # from now on we can choose with which level we want to to continue
            return progress > Ach.__EXAM_DONE_PROGRESS

        elif unlock is Unlocks.ShowEnergy:
            return progress > 0     # Lesson 0 completed

        elif unlock is Unlocks.CircuitReset:
            return progress >= MapConfig.num_of_lessons()    # all lessons completed
        elif unlock is Unlocks.PuzzleFlee:
            return progress >= MapConfig.num_of_lessons()

        elif unlock is Unlocks.ProceedChoice:
            # instead of automatically proceeding to the next level we now have a choice
            return progress > Ach.__EXAM_DONE_PROGRESS

        elif unlock is Unlocks.Spaceship:
            # we can now use the spaceship
            return progress > Ach.__EXAM_DONE_PROGRESS
        elif unlock is Unlocks.Navigation:
            # we can now freely choose between levels in the current world
            return progress > Ach.__EXAM_DONE_PROGRESS
        elif unlock is Unlocks.FreeNavigation:
            # we can now choose between worlds and not only levels in a given world
            return False    # todo implement

        raise NotImplementedError(f"Unlock \"{unlock}\" not implemented yet!")

    @staticmethod
    def is_most_recent_unlock(unlock: Unlocks, progress: int) -> bool:
        if unlock is Unlocks.Spaceship:
            # we can now use the spaceship
            return progress == Ach.__EXAM_DONE_PROGRESS + 1

        raise NotImplementedError(f"Unlock \"{unlock}\" not yet implemented for recency check!")


class AchievementType(enum.Enum):
    World = 0
    Level = 1
    Misc = 2
    Secret = 3  # is not shown until unlocked (therefore also needs to be done in one go, i.e. done_score = 1)
    Story = 4
    Event = 5    # in-level event
    Expedition = 6

    @staticmethod
    def get_display_order() -> "List[AchievementType]":
        return [
            AchievementType.Secret, AchievementType.Misc,
            AchievementType.Expedition, AchievementType.World, AchievementType.Level,
            AchievementType.Story,
        ]


class Achievement:
    __DATA_SEPARATOR = ">q<"

    @staticmethod
    def from_string(text: str) -> "Achievement":
        data = text.split(Achievement.__DATA_SEPARATOR)
        if len(data) == 5:
            name = data[0]
            atype = AchievementType(int(data[1]))
            score = float(data[2])
            done_score = float(data[3])
            return Achievement(name, atype, score, done_score)

    # todo add unlock-date?
    def __init__(self, name: str, atype: AchievementType, score: float, done_score: float):
        self.__name = name
        self.__type = atype
        self.__score = score
        self.__done_score = done_score

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> AchievementType:
        return self.__type

    @property
    def score(self) -> float:
        return self.__score

    @property
    def done_score(self) -> float:
        return self.__done_score

    def is_done(self) -> bool:
        return self.score >= self.done_score

    def add_score(self, score: float) -> bool:  # todo change name to increase_score and make score default to 1?
        """

        :param score: how much score points we want to add
        :return: True if we changed the score, False otherwise
        """
        if score > 0 and not self.is_done():
            self.__score = min(self.score + score, self.done_score)
            return True
        return False

    def to_string(self) -> str:
        text = f"{self.name}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.type.value}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.score}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.done_score}{Achievement.__DATA_SEPARATOR}"
        return text

    def to_display_string(self) -> str:
        if self.is_done():
            text = "[X]"
        else:
            text = "[_]"
        if self.type is AchievementType.Secret:
            text += "???"
        else:
            text += f" {self.name} ({self.score} / {self.done_score})"
        return text


class AchievementManager:
    __DISPLAY_STRING_INDENT = "  "

    def __init__(self, achievements: List[Achievement]):
        self.__storage = {}
        self.__temp_level_storage = {}

        for achievement in achievements:
            self.__storage[achievement.name] = achievement

    @property
    def story_progress(self) -> int:
        return int(self.__storage[Ach.story()].score)

    def __on_achievement_completion(self, achievement: Achievement):
        assert achievement.is_done()

        if achievement.type is AchievementType.Story:
            # add one step to the story achievement since we completed the latest progress
            self.__storage[Ach.story()].add_score(1)

    def check_achievement(self, name: str) -> bool:
        if name in self.__temp_level_storage:
            achievement = self.__temp_level_storage[name]
            return achievement.is_done()
        elif name in self.__storage:
            achievement = self.__storage[name]
            return achievement.is_done()
        elif name.startswith(Unlocks.in_map_reference()):   # so we can check for unlocks in levels and worlds if needed
            unlock_name = name[len(Unlocks.in_map_reference()):].lower()
            for val in Unlocks.__members__.values():
                if val.name.lower() == unlock_name:
                    return Ach.check_unlocks(val, self.story_progress)
            return False
        return False

    def reset_level_events(self):
        self.__temp_level_storage.clear()

    def add_to_achievement(self, name: str, score: float):  # todo maybe default score to 1?
        if name in self.__storage:
            self.__storage[name].add_score(score)

    def trigger_event(self, name: str, score: float = 1):
        if name.startswith(MapConfig.global_event_prefix()):
            name = name[len(MapConfig.global_event_prefix()):]  # remove prefix
            storage = self.__storage
        else:
            storage = self.__temp_level_storage
        if name in storage:
            storage[name].add_score(score)
        else:
            storage[name] = Achievement(name, AchievementType.Event, score, score)

    def progressed_in_story(self, progress: str):
        if progress not in self.__storage:
            self.__storage[progress] = Achievement(progress, AchievementType.Story, 0, 1)
        achievement = self.__storage[progress]
        if achievement.add_score(achievement.done_score):
            self.__on_achievement_completion(achievement)

    def finished_level(self, level: str, display_name: str = None) -> bool:
        if level in self.__storage and self.__storage[level].is_done():
            return False
        else:
            self.__storage[level] = Achievement(level, AchievementType.Level, 1, 1)
            if Ach.is_story_mission(level):
                if display_name is None:
                    self.progressed_in_story(f"{level}_done")
                else:
                    self.progressed_in_story(display_name)
            else:
                self.__on_achievement_completion(self.__storage[level])
            return True

    def finished_world(self, world: str):
        if world not in self.__storage:
            self.__storage[world] = Achievement(world, AchievementType.World, 1, 1)
            self.__on_achievement_completion(self.__storage[world])

    def uncovered_secret(self, name: str):
        if name not in self.__storage:
            self.__storage[name] = Achievement(name, AchievementType.Secret, 1, 1)
            self.__on_achievement_completion(self.__storage[name])

    def to_string(self) -> str:
        text = ""
        for value in self.__storage.values():
            text += f"{value.to_string()}\n"
        return text

    def to_display_string(self) -> str:
        type_text = {}
        for value in self.__storage.values():
            if value.type in type_text:
                type_text[value.type].append(value.to_display_string())
            else:
                type_text[value.type] = [value.to_display_string()]

        text = ""
        # first add the temporary level events
        if len(self.__temp_level_storage) > 0:
            text += f"{AchievementType.Event.name}\n"
            for event in self.__temp_level_storage:
                text += f"{AchievementManager.__DISPLAY_STRING_INDENT}{event.to_display_string()}\n"
        # now add permanent the achievements
        for a_type in AchievementType.get_display_order():
            if a_type in type_text:
                text += f"{a_type.name}\n"
                for achievement in type_text[a_type]:
                    text += f"{AchievementManager.__DISPLAY_STRING_INDENT}{achievement}\n"
        return text
