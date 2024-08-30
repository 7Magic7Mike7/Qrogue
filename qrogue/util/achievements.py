import datetime
import enum
from typing import Optional

from qrogue.util.util_functions import cur_datetime


class Unlocks(enum.Enum):
    # menu unlocks
    MainMenuContinue = (10, "MainMenuContinue")  # unlocked after Level 0

    # hud unlocks
    ShowEnergy = (30, "ShowEnergy")  # unlocked after Level 0

    # puzzle unlocks
    ShowEquation = (55, "ShowEquation")  # whether to show the matrix vector multiplication above the circuit
    PuzzleHistory = ShowEquation    # when checking for PuzzleHistory, the outcome is the same as for ShowEquation
    GateRemove = (52, "GateRemove")  # unlocked automatically
    CircuitReset = (50, "CircuitReset")  # unlocked after Tutorial
    PuzzleFlee = (51, "PuzzleFlee")  # unlocked in Level 1

    # level unlocks
    ProceedChoice = (90, "ProceedChoice")   # unlocked after all Tutorial levels (right before Exam)    # todo: should be available as soon as Level Selection is available
    LevelSelection = (91, "LevelSelection")
    Workbench = (92, "Workbench")
    Expeditions = (93, "Expeditions")

    # internal events
    VisitedWorkbench = (1_001, "VisitedWorkbench")

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
        name = name.lower()  # normalize name
        for unlock in Unlocks:
            if unlock.name.lower() == name:
                return unlock
        return None


class Achievement:
    __DATA_SEPARATOR = ">q<"
    CompletedExpedition = "CompletedExpedition"

    @staticmethod
    def from_string(text: str) -> "Achievement":
        data = text.split(Achievement.__DATA_SEPARATOR)
        if len(data) == 5:
            name = data[0]
            # atype = AchievementType(int(data[1]))
            score = float(data[2])
            done_score = float(data[3])
            return Achievement(name, score, done_score)

    # @staticmethod
    # def from_unlock(unlock: Unlocks) -> "Achievement":
    #    return Achievement(unlock.ach_name, AchievementType.Unlock, 1, 1)

    def __init__(self, name: str, score: float, done_score: float,
                 date_time: Optional[datetime.datetime] = None):
        self.__name = name
        self.__score = score
        self.__done_score = done_score
        # date_time is either the datetime of the last scoring of the achievement or the datetime of completing the
        # achievement (score >= done_score)
        self.__date_time = cur_datetime() if date_time is None else date_time

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> int:  # AchievementType:
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
            self.__date_time = cur_datetime()
            self.__score = min(self.score + score, self.done_score)
            return True
        return False

    def to_string(self) -> str:
        text = f"{self.name}{Achievement.__DATA_SEPARATOR}"
        # text += f"{self.type.value}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.score}{Achievement.__DATA_SEPARATOR}"
        text += f"{self.done_score}{Achievement.__DATA_SEPARATOR}"
        return text

    def to_display_string(self) -> str:
        if self.is_done():
            text = "[X]"
        else:
            text = "[_]"
        # if self.type is AchievementType.Secret:
        #    text += "???"
        # else:
        text += f" {self.name} ({self.score} / {self.done_score})"
        return text

    def __str__(self) -> str:
        return self.to_string()
