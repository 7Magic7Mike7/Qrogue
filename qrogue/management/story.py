import enum
from typing import List

from qrogue.graphics.popups import Popup
from qrogue.management import SaveData
from qrogue.util import ColorConfig, MapConfig
from qrogue.util.help_texts import StoryText, StoryTextType, TutorialText, TutorialTextType


class _StoryProgress(enum.Enum):
    RobotShowcase = 0
    MoonMission = 1
    DarkSideOfMoon = 2

    NewHorizons = 10    # w1 done, now we can travel to new solar systems (other worlds)

    @staticmethod
    def progress_order() -> List["_StoryProgress"]:
        return [
            _StoryProgress.RobotShowcase, _StoryProgress.MoonMission,
            _StoryProgress.DarkSideOfMoon,
            _StoryProgress.NewHorizons,
        ]


class StoryNarration:
    @staticmethod
    def __check_achievement(achievement: str) -> bool:
        return SaveData.instance().achievement_manager.check_achievement(achievement)

    @staticmethod
    def __get_story_progress() -> _StoryProgress:
        progress = _StoryProgress.RobotShowcase

        if StoryNarration.__check_achievement("l1v2"):
            progress = _StoryProgress.DarkSideOfMoon
        elif StoryNarration.__check_achievement(MapConfig.intro_level()):
            progress = _StoryProgress.MoonMission
        return progress

    @staticmethod
    def unlocked_navigation() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.MoonMission)

    @staticmethod
    def completed_tutorial() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.DarkSideOfMoon)

    @staticmethod
    def unlocked_free_navigation() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.NewHorizons)

    @staticmethod
    def entered_navigation():
        progress = StoryNarration.__get_story_progress()
        if progress is _StoryProgress.MoonMission:
            Popup.scientist_says(TutorialText.get(TutorialTextType.Navigation))

    @staticmethod
    def returned_to_spaceship():
        progress = StoryNarration.__get_story_progress()

        if progress is _StoryProgress.RobotShowcase:
            Popup.scientist_says(StoryText.get(StoryTextType.Intro))

        elif progress is _StoryProgress.MoonMission:
            # Popup.scientist_says("They were really impressed by the Robots. So...\n")
            # Popup.scientist_says("They were really impressed by the Robots. So...\nWe will fly to the moon!")
            Popup.scientist_says(StoryText.get(StoryTextType.MoonMission))

    @staticmethod
    def scientist_text() -> str:
        progress = StoryNarration.__get_story_progress()
        if progress is _StoryProgress.RobotShowcase:
            return StoryText.get(StoryTextType.Exam)
        elif progress is _StoryProgress.MoonMission:
            navigation_panel = ColorConfig.highlight_word("Navigation Panel")
            n_tile = ColorConfig.highlight_tile("N")
            return f"The {navigation_panel} {n_tile} is on the left end of the Spaceship."
        return "NO MORE TEXT"
