import unittest
from typing import List

from qrogue.graphics.popups import MultilinePopup
from qrogue.graphics.widgets import ScreenCheckWidgetSet
from qrogue.test import test_util
from qrogue.util import split_text, ColorConfig


class MyTestCase(unittest.TestCase):
    @staticmethod
    def _get_large_level_text() -> str:
        return "\n".join([
            "Now that you know what happens to the //02Circuit Matrix// when applying gates //05in parallel// "
            "(kronecker product), let's see what happens if you apply them //05in series//.",
            "Actually, this is as easy as //05multiplying// two matrices. In the current //02Puzzle// you need to "
            "apply an //02X Gate// first followed by a //02CX Gate//. So we compute a //054x4 matrix// for the "
            "//02X Gate// like before and then //05multiply// the matrix of the //02CX Gate// (note that this is "
            "already a 4x4 matrix since it's a two qubit gate) //05from the left//:",
            "    |00> |01> |10> |11>         |00> |01> |10> |11>         |00> |01> |10> |11>",
            "|00>  1    0    0    0      |00>  0    1    0    0      |00>  0    1    0    0 ",
            "|01>  0    0    0    1   *  |01>  1    0    0    0   =  |01>  0    0    1    0 ",
            "|10>  0    0    1    0      |10>  0    0    0    1      |10>  0    0    0    1 ",
            "|11>  0    1    0    0      |11>  0    0    1    0      |11>  1    0    0    0 ",
            "If we take a look at the result's column //05|00>// (since that's the qubit configuration of our input) "
            "we can see that the resulting matrix indeed //05transforms// this state to //05|11>// which is exactly "
            "the qubit configuration with an amplitude of 1 in the //05Target StateVector//.",
            "",
            "Again, in general the //05order// of multiplication matters. At first glance it may seem "
            "counter-intuitive that the //02Gates// are aligned from //05left to right// in the //02Circuit// but have "
            "to be //05multiplied// from //05right to left//. But if you take a second look at the "
            "//05equation above// your //02Circuit// you can see that the //05Input StateVector// is on the "
            "//05right// side of the matrix. So both the //02Circuit// and the //05calculation// simply consider the "
            "gate/matrix //05closer// to the input first."
        ])

    def _split_compare(self, expected_split: List[str], input_text: str, width: int, padding: int = 0,
                       ignore_padding: bool = False):
        """
        :param ignore_padding: ignores padding for comparison (padding still needs to be set for a correct split!)
        """
        for i, actual_text in enumerate(split_text(input_text, width, padding, test_util.handle_error)):
            if ignore_padding and padding > 0: actual_text = actual_text[padding:-padding]
            self.assertEqual(expected_split[i], actual_text, f"Unexpected text at line #{i}!")
            self.assertEqual(actual_text, actual_text.rstrip(), "Actual text was not rstrip()-ed!")

    def test_splits(self):
        # test split on some handcrafted pseudo-texts and edge cases
        input_text = "abc defg hijkl mnopqr stuvw xyz"
        expected_split = ["abc", "defg", "hijkl", "mnopq", "r", "stuvw", "xyz"]
        self._split_compare(expected_split, input_text, width=5)

        input_text = "\n".join(["Hell sky", "  34 ", "5 7890"])
        expected_split = ["Hell", "sky", "  34", "5", "7890"]
        self._split_compare(expected_split, input_text, width=5)

        input_text = "\n".join(["Hell sky", "  345 7890", "012 3    8", ])
        expected_split = ["Hell", "sky", "  345", "7890", "012 3", "8", ]
        self._split_compare(expected_split, input_text, width=5)

    def test_screen_check_description(self):
        # Screen dimensions used in visual test: (31, 135)
        width = 104  # a width that previously produced incorrect splits
        # the correct splits for the given width
        expected_level = [
            "You should see seven rooms next to each other. While the specific colors don't matter, it is important",
            "to be able to distinguish different elements of the game world (although they also differ in their",
            "character representation).",
            "- //12Pickups// are designed to be //15blue// lower-case characters like //11s//, //11k//, //11c// or "
            "//11g//.",
            "- Tiles containing //12Puzzles// are meant to be //15red// and are //11digits//, //11!//, //11?// and "
            "inverted //11B// for bosses.",
            "- The //12Goal// //11G// of a level and the //12Player Character// //11Q// are usually //15green//.",
            "- Level-shaping tiles like //11#// and //11o// are //15white// inverted",
            "- Lastly, simple //15white// dots //11.// are messages that open Popups",
            "",
            "The last two elements are neutral to the player and, hence, not specifically highlighted (in fact,",
            "they share their color with normal text and UI elements), while the other three are important for",
            "gameplay and should therefore be highlighted."
        ]
        expected_popup = [
            "In the middle of the screen an inverted (i.e., background is the normal text color and text has the",
            "color of normal background) rectangle should have popped up. It has a differently colored headline",
            "followed by text that describes the usage of different colors used inside such Popups. Furthermore,",
            "the bottom left should state \"scroll down\", while the bottom right indicates the number of rows you",
            "can scroll down until the end of the Popup's text is reached. These two bottom elements should also be",
            "highlighted (i.e., different from the colors used inside the Popup)."
        ]
        expected_puzzle = [
            "Here you can see an example of an advanced 3-qubit puzzle. Specifically, there is one matrix followed",
            "by three vertical vectors.",
            "Overall they should contain five different colors:",
            f"- //92headlines// of matrix and vectors (~Circuit Matrix~, ~In~, ~Out~, ~Target~)",
            f"- //93|000>// to //93|111>// (called ket-notation) labeling columns and rows",
            "- first two entries of ~Out~, indicating //90incorrect values//",
            "- last six entries of ~Out~, indicating //91correct values//",
            "- other matrix/vector entries are in default color (i.e., the same as non-highlighted UI elements)",
            "",
            "If you cannot see all eight rows or columns of the matrix, press //14M// to open a popup for suggested",
            "solutions.",
        ]

        self._split_compare(expected_level, ScreenCheckWidgetSet.level_description(), width, 1, ignore_padding=True)
        self._split_compare(expected_popup, ScreenCheckWidgetSet.popup_description(), width, 1, ignore_padding=True)
        self._split_compare(expected_puzzle, ScreenCheckWidgetSet.puzzle_description(), width, 1, ignore_padding=True)

    def test_small_message_split(self):
        # test split on a small in-game message (l0k0v0, *keyFound)
        # Screen dimensions used in visual test: (31, 135)
        dimensions = 11, 100  # Popup dimensions retrieved from visual tests
        padding = 2
        # don't use our padding because it is already considered in __split_compare()
        width = MultilinePopup.popup_width_to_content_width(dimensions[1], padding=0)
        input_text = "Great, you found a //02Key//. The //05number of keys// you hold is displayed in the //05HUD// " \
                     "on the //05top left//."
        expected_split = [
            "Great, you found a //02Key//. The //05number of keys// you hold is displayed in the //05HUD// on the "
            "//05top//",
            "//05left//.",
        ]
        self._split_compare(expected_split, input_text, width, padding, ignore_padding=True)

    def test_large_message_split(self):
        # test split on a large in-game message
        # Screen dimensions used in visual test: (31, 135)
        dimensions = 11, 100  # Popup dimensions retrieved from visual tests
        padding = 2
        # don't use our padding because it is already considered in __split_compare()
        width = MultilinePopup.popup_width_to_content_width(dimensions[1], padding=0)
        input_text = self._get_large_level_text()
        # according to dimensions, and padding the content-width is 90 (max num of printed characters per line)
        expected_split = [
            "Now that you know what happens to the //02Circuit Matrix// when applying gates //05in parallel//",
            "(kronecker product), let's see what happens if you apply them //05in series//.",
            "Actually, this is as easy as //05multiplying// two matrices. In the current //02Puzzle// you need to",
            "apply an //02X Gate// first followed by a //02CX Gate//. So we compute a //054x4 matrix// for the " +
            "//02X Gate//",
            "like before and then //05multiply// the matrix of the //02CX Gate// (note that this is already a 4x4",
            "matrix since it's a two qubit gate) //05from the left//:",
            "    |00> |01> |10> |11>         |00> |01> |10> |11>         |00> |01> |10> |11>",
            "|00>  1    0    0    0      |00>  0    1    0    0      |00>  0    1    0    0",
            "|01>  0    0    0    1   *  |01>  1    0    0    0   =  |01>  0    0    1    0",
            "|10>  0    0    1    0      |10>  0    0    0    1      |10>  0    0    0    1",
            "|11>  0    1    0    0      |11>  0    0    1    0      |11>  1    0    0    0",
            "If we take a look at the result's column //05|00>// (since that's the qubit configuration of our",
            "input) we can see that the resulting matrix indeed //05transforms// this state to //05|11>// which is",
            "exactly the qubit configuration with an amplitude of 1 in the //05Target StateVector//.",
            "",
            "Again, in general the //05order// of multiplication matters. At first glance it may seem",
            "counter-intuitive that the //02Gates// are aligned from //05left to right// in the //02Circuit// but " +
            "have to",
            "be //05multiplied// from //05right to left//. But if you take a second look at the //05equation above// " +
            "your",
            "//02Circuit// you can see that the //05Input StateVector// is on the //05right// side of the matrix. So " +
            "both",
            "the //02Circuit// and the //05calculation// simply consider the gate/matrix //05closer// to the input " +
            "first."
        ]

        self._split_compare(expected_split, input_text, width, padding, ignore_padding=True)

    def test_highlight_splits(self):
        def highlight(text: str):
            return ColorConfig.highlight_object(text)

        width = 10
        input_text = f"{highlight('abcdefghij')} ab{highlight('cd')} {highlight('fghij')} " \
                     f"   {highlight(' bcdefgh')} {highlight('jkl')}"
        expected_split = [highlight("abcdefghij"), f"ab{highlight('cd')} {highlight('fghij')}",
                          f"{highlight(' bcdefgh')}", highlight("jkl")]
        self._split_compare(expected_split, input_text, width)

        input_text = f"ab def {highlight('hijde')} ghi {highlight('a cd')} {highlight('fg ijcd')} fgh j " \
                     f"abc {highlight('ef hijde')} {highlight('ghij')}"
        expected_split = [
            f"ab def",
            f"{highlight('hijde')} ghi",
            f"{highlight('a cd')} {highlight('fg')}",
            f"{highlight('ijcd')} fgh j",
            f"abc {highlight('ef')}",
            f"{highlight('hijde')} {highlight('ghij')}"
        ]
        self._split_compare(expected_split, input_text, width)


if __name__ == '__main__':
    unittest.main()
