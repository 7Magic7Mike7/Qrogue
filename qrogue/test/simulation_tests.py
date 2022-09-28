import os.path
import sys

from qrogue.qrogue import simulate_game
from qrogue.util import PathConfig


def test_run(user_data_path: str):
    sim_path = os.path.join(user_data_path, PathConfig.keylog_folder(), "lesson1.qrkl")
    simulate_game(sim_path, from_console=True, debugging=True)


user_data_path = sys.argv[1]
test_run(user_data_path)
