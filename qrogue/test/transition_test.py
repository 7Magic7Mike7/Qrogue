import unittest
from typing import List, Optional

from qrogue.graphics.widgets import TransitionWidgetSet
from qrogue.management import QrogueCUI
from qrogue.test import test_util


class _TestQrogueCUI(QrogueCUI):
    @staticmethod
    def exam_spaceship() -> List[TransitionWidgetSet.TextScroll]:
        return [
            TransitionWidgetSet.TextScroll.hasty("A couple of days later...", text_delay=0.5),
            TransitionWidgetSet.TextScroll.fast("Mike received a letter stating he was chosen to join Mission "
                                                "Quniverse!", clear_previous=True),
        ]

    def start(self, level_name: Optional[str] = None):
        text_scrolls = self.exam_spaceship()
        self._execute_transition(text_scrolls, QrogueCUI._State.Menu, None, additional_callback=self.stop)
        super().start()


class TransitionTests(test_util.SingletonSetupTestCase):
    def test_transition(self):
        _TestQrogueCUI(7).start()


if __name__ == "__main__":
    unittest.main()
