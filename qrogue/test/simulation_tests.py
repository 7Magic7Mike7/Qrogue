import os.path
import shutil
import unittest
from typing import List, Optional

from qrogue.management import QrogueCUI, NewSaveData
from qrogue.test import test_util
from qrogue.util import Logger, FileTypes, PathConfig, TestConfig
from qrogue.util.game_simulator import GameSimulator

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
        def __init__(self, file_name: str, in_keylog_folder: bool = False, automate: bool = True,
                     auto_scroll_transitions: bool = True, stop_when_finished: bool = True):
            self.__name = file_name
            self.__path = file_name if in_keylog_folder else os.path.join("test_data", "keylogs", file_name)
            self.__in_keylog_folder = in_keylog_folder
            self.__automate = automate
            self.__auto_scroll_transitions = auto_scroll_transitions
            self.__stop_when_finished = stop_when_finished

        @property
        def name(self) -> str:
            return self.__name

        def start(self) -> Optional[NewSaveData]:
            if self.__automate: automation_time_step = TestConfig.automation_step_time()
            else: automation_time_step = None
            return QrogueCUI.start_simulation(self.__path, self.__in_keylog_folder, automation_time_step,
                                              self.__auto_scroll_transitions, self.__stop_when_finished)

        def to_string(self) -> str:
            simulator = GameSimulator(self.__path, self.__in_keylog_folder)
            simulator.set_controls(test_util.get_dummy_controls())
            return simulator.to_string(skip_header=True)

        def __str__(self):
            return f"Simulation \"{self.name}\" @{self.__path} (" \
                   f"{'in' if self.__in_keylog_folder else 'out'}side, " \
                   f"{'auto' if self.__automate else 'manual'}, " \
                   f"{'stop' if self.__stop_when_finished else 'continue'})"

    @staticmethod
    def load_save_data(file_name: str) -> NewSaveData:
        path = os.path.join("test_data", "saves", file_name)
        return NewSaveData.load(path, in_user_path=False)

    def compare_save_data(self, a: NewSaveData, b: NewSaveData):
        gate_diff, level_diff, unlocks_diff, ach_diff = a.compare(b)
        self.assertEqual(0, len(gate_diff), f"There is a difference in stored Gates: "
                                            f"{[str(gate) for gate in gate_diff]}")
        self.assertEqual(0, len(level_diff), f"There is a difference in completed Levels: "
                                             f"{[level for level in level_diff]}")
        self.assertEqual(0, len(unlocks_diff), f"There is a difference in discovered Unlocks: "
                                               f"{[str(unlock) for unlock in unlocks_diff]}")
        self.assertEqual(0, len(ach_diff), f"There is a difference in Achievements: "
                                           f"{[str(ach) for ach in ach_diff]}")

    def test_meta(self):
        simulations: List[SimulationTestCase._Simulation] = [
            #SimulationTestCase._Simulation("fresh_l1-2"),
            #SimulationTestCase._Simulation("25032024_152548_meta716940"),
            #SimulationTestCase._Simulation("21032024_163055_meta248180"),
        ]
        for simulation in simulations:
            simulation.start()

    def test_level(self):
        index: Optional[int] = 0
        simulations: List[SimulationTestCase._Simulation] = [
            SimulationTestCase._Simulation("simple_l0k0v0"),
            SimulationTestCase._Simulation("simple_l0k0v1"),
            SimulationTestCase._Simulation("simple_l0k0v2"),
            SimulationTestCase._Simulation("simple_l0k0v3"),
            SimulationTestCase._Simulation("simple_l0k0v4"),
        ]
        for i, simulation in enumerate(simulations):
            if index is not None and i != index: continue

            try:
                save_data = simulation.start()
                post_save_data = self.load_save_data(f"post_l0k0v{i}")
                self.compare_save_data(save_data, post_save_data)
                self.compare_save_data(post_save_data, save_data)
            except AssertionError as ae:
                print()
                print("####################################################")
                print("####################### ERROR ######################")
                print("####################################################")
                print(ae)
                print()
                print("----------------------------------------------------")
                print("----------------------- LOGS -----------------------")
                print("----------------------------------------------------")
                print()
                Logger.instance().flush()


if __name__ == '__main__':
    unittest.main()
