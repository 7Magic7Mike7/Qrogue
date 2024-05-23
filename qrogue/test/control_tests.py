import unittest
from typing import Optional

import py_cui

from qrogue.test import test_util
from qrogue.util import Controls, Keys


class ControlTests(unittest.TestCase):
    def __test_key(self, controls: Controls, logical_key: Keys, physical_key: int, visual_key: str,
                   category: Optional[str] = None):
        """
        :param logical_key: QRogue's internal representation of the key
        :param physical_key: value of the physical key pressed on the keyboard (PyCUI internal representation)
        :param visual_key: text to show how a human would refer to the key
        :param category: optional description of the key's category for a more readable assertion
        """
        keys = controls.get_keys(logical_key)

        if category is None:
            self.assertTrue(physical_key in keys)
        else:
            self.assertTrue(physical_key in keys, f"{visual_key} not set as {category}-Key!")

        space_index = keys.index(physical_key)
        self.assertEqual(visual_key, controls.to_keyboard_string(logical_key, space_index))

    def test_keyboard_strings(self):
        controls = test_util.get_dummy_controls()

        # test simple letter key
        matrix_popup_keys = controls.get_keys(Keys.MatrixPopup)
        self.assertEqual(1, len(matrix_popup_keys), f"More than one MatrixPopup-Key available: {matrix_popup_keys}!")
        self.assertEqual(py_cui.keys.KEY_M_LOWER, matrix_popup_keys[0], "MatrixPopup-Key is not as expected!")
        self.assertEqual("m".upper(), controls.to_keyboard_string(Keys.MatrixPopup),
                         "Keyboard string for MatrixPopup-Key not as expected!")

        # test simple digit key (hotkey)
        self.__test_key(controls, Keys.HotKey1, py_cui.keys.KEY_1, "1", "Hotkey1")

        # test non-letter key
        self.__test_key(controls, Keys.Action, py_cui.keys.KEY_SPACE, " ", "Action")
        self.__test_key(controls, Keys.Pause, py_cui.keys.KEY_TAB, "\t", "Pause")

        # test non-printable key
        # self.__test_key(controls, Keys.MoveDown, py_cui.keys.KEY_DOWN_ARROW, "???", "MoveDown")


if __name__ == '__main__':
    unittest.main()
