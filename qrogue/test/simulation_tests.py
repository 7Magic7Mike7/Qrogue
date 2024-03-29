import os.path
import shutil
import unittest
from typing import List, Optional

from qrogue.management import QrogueCUI, NewSaveData
from qrogue.test import test_util
from qrogue.util import PathConfig, Logger, FileTypes, Config, TestConfig

user_data_path = os.path.join(os.path.dirname(__file__), "user_data")


def cleanup() -> bool:
    if os.path.exists(user_data_path):
        try:
            shutil.rmtree(user_data_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (user_data_path, e))
            return False
    return True


def setup() -> bool:
    # activate testing
    TestConfig.activate()
    TestConfig.set_automation()

    # create the needed folder structure
    try:
        os.mkdir(user_data_path)
        keylogs_dir = os.path.join(user_data_path, PathConfig.keylog_folder())
        os.mkdir(keylogs_dir)

        dir_path = os.path.join(os.path.dirname(__file__), "test_data", "keylogs")
        for file in os.listdir(dir_path):
            if file.endswith(FileTypes.KeyLog.value):
                shutil.copy(os.path.join(dir_path, file), keylogs_dir)
    except shutil.SameFileError:
        return False

    return True


class SimulationTestCase(test_util.SingletonSetupTestCase):
    class _Simulation:
        def __init__(self, path: str, in_keylog_folder: bool = False, automate: bool = True,
                     auto_scroll_transitions: bool = True, stop_when_finished: bool = True):
            self.__path = path if in_keylog_folder else os.path.join("test_data", "keylogs", path)
            self.__in_keylog_folder = in_keylog_folder
            self.__automate = automate
            self.__auto_scroll_transitions = auto_scroll_transitions
            self.__stop_when_finished = stop_when_finished

        def start(self) -> Optional[NewSaveData]:
            return QrogueCUI.start_simulation(self.__path, self.__in_keylog_folder, self.__automate,
                                              self.__auto_scroll_transitions, self.__stop_when_finished)

        def to_string(self) -> str:
            simulator = GameSimulator(self.__path, self.__in_keylog_folder)
            simulator.set_controls(test_util.get_dummy_controls())
            return simulator.to_string(skip_header=True)

        def __str__(self):
            return f"Simulation @{self.__path} (" \
                   f"{'in' if self.__in_keylog_folder else 'out'}side, " \
                   f"{'auto' if self.__automate else 'manual'}, " \
                   f"{'stop' if self.__stop_when_finished else 'continue'})"

    def test_meta(self):
        simulations: List[SimulationTestCase._Simulation] = [
            #SimulationTestCase._Simulation("25032024_153036_meta184705"),
            #SimulationTestCase._Simulation("25032024_152548_meta716940"),
            #SimulationTestCase._Simulation("21032024_163055_meta248180"),
        ]
        for simulation in simulations:
            simulation.start()

    def test_level(self):
        simulations: List[SimulationTestCase._Simulation] = [
            SimulationTestCase._Simulation("l0k0v0_simple"),
            #SimulationTestCase._Simulation("l0k0v1_simple"),
        ]
        for simulation in simulations:
            simulation.start()


if __name__ == '__main__':
    unittest.main()
