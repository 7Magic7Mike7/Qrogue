import enum

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


class Achievement:
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


class AchievementManager:
    def __init__(self):
        self.__storage = {}
        self.__temp_level_storage = {}

        # todo load from file
        self.__storage[FinishedTutorial] = Achievement(FinishedTutorial, AchievementType.Tutorial, 0, 1)
        self.__storage[EnteredPauseMenu] = Achievement(EnteredPauseMenu, AchievementType.Tutorial, 0, 1)
        self.__storage[CompletedExpedition] = Achievement(CompletedExpedition, AchievementType.Expedition, 0, 1000)

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
