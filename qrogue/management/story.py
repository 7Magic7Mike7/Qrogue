import enum
from typing import List

from qrogue.graphics.popups import Popup
from qrogue.management import SaveData
from qrogue.util import ColorConfig, MapConfig


class _StoryProgress(enum.Enum):
    RobotShowcase = 0
    MoonMission = 1
    EntangledMars = 2

    NewHorizons = 10    # w1 done, now we can travel to new solar systems (other worlds)

    @staticmethod
    def progress_order() -> List["_StoryProgress"]:
        return [
            _StoryProgress.RobotShowcase, _StoryProgress.MoonMission,
            _StoryProgress.EntangledMars,
            _StoryProgress.NewHorizons,
        ]


class StoryNarration:

    @staticmethod
    def __check_achievement(achievement: str) -> bool:
        return SaveData.instance().achievement_manager.check_achievement(achievement)

    @staticmethod
    def __get_story_progress() -> _StoryProgress:
        progress = _StoryProgress.RobotShowcase
        if StoryNarration.__check_achievement(MapConfig.intro_level()):
            progress = _StoryProgress.MoonMission

        return progress

    @staticmethod
    def __intro() -> str:
        finally_ = ColorConfig.highlight_word("finally")
        r_tile = ColorConfig.highlight_tile("R")
        arrow_keys = ColorConfig.highlight_key("Arrow Keys")
        wasd_keys = ColorConfig.highlight_key("WASD")
        space = ColorConfig.highlight_key("Space")
        enter = ColorConfig.highlight_key("Enter")
        return f"Hey Mike, the time has {finally_} come! Quick, join me over here!\n\n" \
               f"[Move to the blue {r_tile} with {arrow_keys} or {wasd_keys} and close this dialog with {space} or " \
               f"{enter}]"

    @staticmethod
    def unlocked_navigation() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.MoonMission)

    @staticmethod
    def completed_tutorial() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.EntangledMars)

    @staticmethod
    def unlocked_free_navigation() -> bool:
        progress = StoryNarration.__get_story_progress()
        ordered_progress = _StoryProgress.progress_order()
        return ordered_progress.index(progress) >= ordered_progress.index(_StoryProgress.NewHorizons)

    @staticmethod
    def entered_navigation():
        progress = StoryNarration.__get_story_progress()
        if progress is _StoryProgress.MoonMission:
            l_tile = ColorConfig.highlight_tile("L")
            l2_tile = ColorConfig.highlight_tile("L - 2")
            moon = ColorConfig.highlight_word("Moon")
            msg_tile = ColorConfig.highlight_tile(".")
            t_tile = ColorConfig.highlight_tile("t")
            Popup.scientist_says(f"In the navigation view you can see rooms representing the different locations "
                                 f"{l_tile} we can navigate to. E.g. at the top of the room to the right you can see "
                                 f"{l2_tile} which represents our current destination: the {moon}. Aside from the "
                                 f"number of the location each room also has a description of the location you can "
                                 f"access by moving onto {msg_tile} as well as {t_tile} to actually travel there.\n"
                                 f"Right now you are in the navigation hub where you can find a general description "
                                 f"and {t_tile} will exit the navigation view.\n"
                                 f"PS: Later we can also go back to earth to redo our previous task - but right "
                                 f"now there is an exciting moon mission and we don't want to waste any more time!")

    @staticmethod
    def returned_to_spaceship():
        progress = StoryNarration.__get_story_progress()

        if progress is _StoryProgress.RobotShowcase:
            Popup.scientist_says(StoryNarration.__intro())

        elif progress is _StoryProgress.MoonMission:
            navigation_panel = ColorConfig.highlight_word("Navigation Panel")
            n_tile = ColorConfig.highlight_tile("N")
            Popup.scientist_says("They were really impressed by the Robots. So...\n")
            Popup.scientist_says("They were really impressed by the Robots. So...\nWe will fly to the moon!")
            Popup.scientist_says("They were really impressed by the Robots. So...\nWe will fly to the moon!\n"
                                 f"Currently we are still orbiting earth, so please go over to the {navigation_panel} "
                                 f"{n_tile}.")

    @staticmethod
    def scientist_text() -> str:
        progress = StoryNarration.__get_story_progress()
        if progress is _StoryProgress.RobotShowcase:
            q_tile = ColorConfig.highlight_tile("Q")
            return "We can finally present the full potential of our Circuit-Robots! And if the authority sees how " \
                   "good you are at controlling them, they'll even let us join the upcoming moon mission!!\n" \
                   "...\n" \
                   "You look still a bit tired... but no worries, I will guide you through it step by step!\n" \
                   f"Move onto the {q_tile} on the bottom to start."
        elif progress is _StoryProgress.MoonMission:
            navigation_panel = ColorConfig.highlight_word("Navigation Panel")
            n_tile = ColorConfig.highlight_tile("N")
            return f"The {navigation_panel} {n_tile} is on the left end of the Spaceship."
        return "NO MORE TEXT"
