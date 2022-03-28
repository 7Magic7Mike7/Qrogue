import enum
from typing import List

FinishedTutorial = "CompletedTutorial"
EnteredPauseMenu = "EnteredPauseMenu"
FirstDoorUnlocked = "UnlockedDoor"
CompletedExpedition = "CompletedExpedition"


class AchievementType(enum.Enum):
    World = 0
    Level = 1
    Gate = 2
    Secret = 3  # is not shown until unlocked (therefore also needs to be done in one go, i.e. done_score = 1)
    Tutorial = 4
    Event = 5    # in-level event
    Expedition = 6

    @staticmethod
    def get_display_order() -> "List[AchievementType]":
        return [
            AchievementType.Secret, AchievementType.Gate,
            AchievementType.Expedition, AchievementType.World, AchievementType.Level,
            AchievementType.Tutorial,
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

    def add_score(self, score: float):
        if score > 0:
            self.__score += score

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
    __DISPLAY_STRING_IDENT = "  "

    def __init__(self, achievements: List[Achievement]):
        self.__storage = {}
        self.__temp_level_storage = {}

        for achievement in achievements:
            self.__storage[achievement.name] = achievement

    def check_achievement(self, name: str) -> bool:
        if name in self.__temp_level_storage:
            achievement = self.__temp_level_storage[name]
            return achievement.is_done()
        elif name in self.__storage:
            achievement = self.__storage[name]
            return achievement.is_done()
        return False

    def reset_level_events(self):
        self.__temp_level_storage.clear()

    def add_to_achievement(self, name: str, score: float):
        if name in self.__storage:
            self.__storage[name].add_score(score)

    def trigger_level_event(self, name: str, score: float = 1):
        if name in self.__temp_level_storage:
            self.__temp_level_storage[name].add_score(score)
        else:
            self.__temp_level_storage[name] = Achievement(name, AchievementType.Event, score, 1)

    def finished_tutorial(self, tutorial: str):
        self.__storage[tutorial] = Achievement(tutorial, AchievementType.Tutorial, 1, 1)

    def finished_level(self, level: str):
        self.__storage[level] = Achievement(level, AchievementType.Level, 1, 1)
        if not self.check_achievement(FinishedTutorial):
            self.finished_tutorial(FinishedTutorial)

    def finished_world(self, world: str):
        self.__storage[world] = Achievement(world, AchievementType.World, 1, 1)

    def uncovered_secret(self, name: str):
        if name not in self.__storage:
            self.__storage[name] = Achievement(name, AchievementType.Secret, 1, 1)

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
                text += f"{AchievementManager.__DISPLAY_STRING_IDENT}{event.to_display_string()}\n"
        # now add permanent the achievements
        for a_type in AchievementType.get_display_order():
            if a_type in type_text:
                text += f"{a_type.name}\n"
                for achievement in type_text[a_type]:
                    text += f"{AchievementManager.__DISPLAY_STRING_IDENT}{achievement}\n"
        return text
