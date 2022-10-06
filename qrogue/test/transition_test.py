from qrogue.graphics.widgets import TransitionWidgetSet
from qrogue.management import QrogueCUI, TransitionText


class TestQrogueCUI(QrogueCUI):
    def __init__(self, seed: int):
        super().__init__(seed)

    def start(self):
        text_scrolls = [
            TransitionWidgetSet.TextScroll.medium("Welcome to the great", clear_previous=True),
            TransitionWidgetSet.TextScroll.instant(" \"Mission Quniverse\".", text_delay=0.5),
            TransitionWidgetSet.TextScroll.hasty("\nWe hope you'll like it - bye!", text_delay=1, clear_previous=True)
        ]
        text_scrolls = TransitionText.exam_spaceship()
        self._execute_transition(text_scrolls, QrogueCUI._State.Menu, self.seed, additional_callback=self.stop)
        super(TestQrogueCUI, self).start()


TestQrogueCUI(7).start()
