from typing import Callable

from qrogue.util import achievements, ColorConfig


class ScientistTexts:
    __check_event = None

    @staticmethod
    def set_check_achievement(check_achievement: Callable[[str], bool]):
        ScientistTexts.__check_event = check_achievement

    @staticmethod
    def intro() -> str:
        finally_ = ColorConfig.highlight_word("finally")
        r_tile = ColorConfig.highlight_tile("R")
        arrow_keys = ColorConfig.highlight_key("Arrow Keys")
        wasd_keys = ColorConfig.highlight_key("WASD")
        space = ColorConfig.highlight_key("Space")
        return f"Hey Mike, the time has {finally_} come! Quick, join me over here!\n\n" \
               f"[Move to the blue {r_tile} with {arrow_keys} or {wasd_keys} and close this dialog with {space}]"

    @staticmethod
    def navigation() -> str:
        return ""

    @staticmethod
    def get() -> str:
        if not ScientistTexts.__check_event(achievements.FinishedTutorial):
            navigation_panel = ColorConfig.highlight_word("Navigation Panel")
            n_tile = ColorConfig.highlight_tile("N")
            return "We can finally test the full potential of our Circuit-Robots! And if we succeed in the simulated " \
                   "environment, we will be able to join the upcoming moon mission.\n" \
                   "...\n" \
                   "You look still a bit tired... but no worries, I will guide you through the final test step by " \
                   "step!\n" \
                   f"First go to the {navigation_panel} {n_tile} on the left side."

        return "NO MORE TEXT"
