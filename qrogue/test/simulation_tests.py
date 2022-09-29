import os.path
import shutil
from typing import List

from qrogue.management import QrogueCUI
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


def start_simulation(simulation_path: str):
    if PathConfig.load_paths(None, user_data_path):
        return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    else:
        return_code = 1

    if return_code == 0:
        Config.activate_debugging()
        QrogueCUI.start_simulation_test(simulation_path)
    return return_code


def test_run() -> List[int]:
    paths = [
        "lesson0.qrkl",
        "lesson1.qrkl",
    ]
    error_counts = []
    for p in paths:
        if not p.endswith(FileTypes.KeyLog.value):
            p += FileTypes.KeyLog.value
        sim_path = os.path.join(user_data_path, PathConfig.keylog_folder(), p)
        return_code = start_simulation(sim_path)
        if return_code == 0:
            error_counts.append(Logger.instance().error_count)
        else:
            print(f"ERROR: trying to simulate \"{sim_path}\" returned {return_code}")
            error_counts.append(1)

    return error_counts


assert cleanup(), "Exception occurred during cleanup!"
assert setup(), "Exception occurred during setup!"

error_counts = test_run()
assert sum(error_counts) <= 0, f"test_run() returned with errors: {error_counts}"

assert cleanup(), "Exception occurred during cleanup!"


print("Simulation tests succeeded!")
