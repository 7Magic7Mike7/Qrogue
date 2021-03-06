import enum

from qrogue.graphics.popups import Popup
from qrogue.management import SaveData
from qrogue.util import ColorConfig
from qrogue.util.help_texts import StoryText, StoryTextType, TutorialText, TutorialTextType


class _StoryProgress(enum.Enum):
    RobotShowcase = 0
    MoonMission = 1
    DarkSideOfMoon = 2
    FirstExpedition = 3

    NewHorizons = 10    # w0 done, now we can travel to new solar systems (other worlds)


class StoryNarration:

    # TODO: Incorporate into new level structure

    @staticmethod
    def entered_navigation():
        progress = SaveData.instance().story_progress

        if progress is _StoryProgress.MoonMission:
            Popup.scientist_says(TutorialText.get(TutorialTextType.Navigation))

        elif progress is _StoryProgress.FirstExpedition:
            Popup.scientist_says("Move down to go on an expedition.")

    @staticmethod
    def returned_to_spaceship():
        progress = SaveData.instance().story_progress

        if progress is _StoryProgress.RobotShowcase:
            Popup.scientist_says(StoryText.get(StoryTextType.Intro))

        elif progress is _StoryProgress.MoonMission:
            # Popup.scientist_says("They were really impressed by the Robots. So...\n")
            # Popup.scientist_says("They were really impressed by the Robots. So...\nWe will fly to the moon!")
            Popup.scientist_says(StoryText.get(StoryTextType.MoonMission))

        elif progress is _StoryProgress.FirstExpedition:
            Popup.scientist_says(StoryText.get(StoryTextType.DarkSideOfMoon))

    @staticmethod
    def scientist_text() -> str:
        progress = SaveData.instance().story_progress

        if progress is _StoryProgress.RobotShowcase:
            return StoryText.get(StoryTextType.Exam)

        elif progress is _StoryProgress.MoonMission:
            navigation_panel = ColorConfig.highlight_word("Navigation Panel")
            n_tile = ColorConfig.highlight_tile("N")
            return f"The {navigation_panel} {n_tile} is on the left end of the Spaceship."

        return "NO MORE TEXT"
