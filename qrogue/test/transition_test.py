from typing import List

from qrogue.graphics.widgets import TransitionWidgetSet
from qrogue.management import QrogueCUI
from qrogue.util import Config


class TestQrogueCUI(QrogueCUI):
    @staticmethod
    def exam_spaceship() -> List[TransitionWidgetSet.TextScroll]:
        return [
            TransitionWidgetSet.TextScroll.hasty("A couple of days later...", text_delay=0.5),
            TransitionWidgetSet.TextScroll.fast("Mike received a letter stating he was chosen to join Mission Quniverse!",
                                                clear_previous=True),
        ]

    def __init__(self, seed: int):
        super().__init__(seed)

    def start(self):
        text_scrolls = [
            TransitionWidgetSet.TextScroll.medium("Welcome to the great", clear_previous=True),
            TransitionWidgetSet.TextScroll.instant(" \"Mission Quniverse\".", text_delay=0.5),
            TransitionWidgetSet.TextScroll.hasty("\nWe hope you'll like it - bye!", text_delay=1, clear_previous=True)
        ]
        text_scrolls = TestQrogueCUI.exam_spaceship()
        self._execute_transition(text_scrolls, QrogueCUI._State.Menu, self.seed, additional_callback=self.stop)
        super(TestQrogueCUI, self).start()


def transition_test():
    TestQrogueCUI(7).start()


if __name__ == "__main__":
    Config.activate_debugging()
    transition_test()
