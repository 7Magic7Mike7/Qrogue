import enum


class AchievementType(enum.Enum):
    World = 0
    Level = 1
    Gate = 2
    Secret = 3  # is not shown until unlocked (therefore also needs to be done in one go, i.e. done_score = 1)


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

    def add_to_achievement(self, name: str, score: float):
        if name in self.__storage:
            self.__storage[name].add_score(score)

    def finished_level(self, level: str):
        self.__storage[level] = Achievement(level, AchievementType.Level, 1, 1)

    def finished_world(self, world: str):
        self.__storage[world] = Achievement(world, AchievementType.World, 1, 1)

    def uncovered_secret(self, name: str):
        if name not in self.__storage:
            self.__storage[name] = Achievement(name, AchievementType.Secret, 1, 1)

