import os.path
import unittest
from typing import List

from py_cui import PyCUI

from qrogue.management import NewSaveData
from qrogue.util import Controls, Keys
from qrogue.util.game_simulator import GameSimulator
from qrogue.util.key_logger import KeyLogger


class KeyLoggingTestCase(unittest.TestCase):
    class _TestKeyLogger(KeyLogger):
        @staticmethod
        def write(path: str, text: str):
            with open(path, "w") as file:
                file.write(text)

        def __init__(self):
            super().__init__(self.write)

        def flush_if_useful(self):
            # always flush since minimum length or other criteria might not be fulfilled for some test cases
            self._flush(force=True)

    class _TestCUI(PyCUI):
        def __init__(self, key_logger: KeyLogger):
            super().__init__(1, 1)
            self.__controls = Controls(self._handle_key_presses)
            self.__key_logger = key_logger
            self.__pressed_keys: List[int] = []     # also store the raw key-press

        @property
        def controls(self) -> Controls:
            return self.__controls

        @property
        def pressed_keys(self) -> List[int]:
            return list(self.__pressed_keys)

        def _handle_key_presses(self, key_pressed: int) -> None:
            self.__pressed_keys.append(key_pressed)
            self.__key_logger.log(self.__controls, key_pressed)

    def test_simple(self):
        save_path = os.path.join("test_data", "dynamic_data", "test.qrkl")
        key_logger = KeyLoggingTestCase._TestKeyLogger()
        key_logger.reinit(7, "TEST", NewSaveData.empty_save_state(), save_path)
        cui = KeyLoggingTestCase._TestCUI(key_logger)

        logical_keys = [key for key in Keys]
        for invalid_key in Keys.invalid_values(): logical_keys.remove(invalid_key)  # remove invalid ("meta") keys
        raw_keys = []
        for key in Keys:
            if key not in Keys.invalid_values():    # remove invalid ("meta") keys
                raw_keys.append(cui.controls.get_key(key))

        # test if handle() correctly returns the raw (PyCUI-internal) key for all our logical keys
        # this also treats these keys as pressed and stores them in our KeyLogger
        for i, key in enumerate(logical_keys):
            self.assertEqual(raw_keys[i], cui.controls.handle(key), "Unexpected PyCUI key!")

        # test if all raw keys were stored (not testing logging yet!) correctly
        self.assertEqual(len(raw_keys), len(cui.pressed_keys), "Different number of pressed keys!")
        for i in range(len(raw_keys)):
            self.assertEqual(raw_keys[i], cui.pressed_keys[i], f"Different key pressed @{i}!")

        key_logger.flush_if_useful()    # flush stored data

        # now test if all keys were logged correctly
        simulator = GameSimulator(save_path, in_keylog_folder=False)
        simulator.set_controls(cui.controls)

        # first the simulator needs to close its informative popup
        sim_start_key = cui.controls.encode(simulator.next())
        self.assertEqual(Keys.PopupClose, sim_start_key, "Popup was not closed!")

        # now test if all logged keys are equivalent (cannot test for "same" since logical keys can share raw keys, and
        # we therefore loose information when pressing a key) to the original logical key in regard to the actual
        # pressed key
        for i, pressed_key in enumerate(cui.pressed_keys):
            # encode the next (raw-equivalent) key to its logical counterpart
            logged_logical_key = cui.controls.encode(simulator.next())
            self.assertTrue(cui.controls.are_equivalent(logical_keys[i], logged_logical_key, pressed_key))
        self.assertEqual(None, simulator.next(), "Simulator not finished!")


if __name__ == '__main__':
    unittest.main()
