
import random
import sys

import py_cui.errors

from qrogue.game.game import GameHandler
from qrogue.util.config import Config
from qrogue.util.logger import Logger


def start_game():
    __CONSOLE_ARGUMENT = "--from-console"
    __DEBUG_ARGUMENT = "--debug"

    return_code = Config.load()  # NEEDS TO BE THE FIRST THING WE DO!
    if return_code == 0:
        if __DEBUG_ARGUMENT in sys.argv:
            Config.activate_debugging()
        seed = random.randint(0, Config.MAX_SEED)
        print(f"[Qrogue] Starting game with seed = {seed}")
        try:
            game = GameHandler(seed)
            game.start()
        except py_cui.errors.PyCUIOutOfBoundsError:
            #print("[Qrogue] ERROR!")
            #print("Your terminal window is too small. "
            #      "Please make it bigger (i.e. maximize it) or reduce the font size.")
            print("---------------------------------------------------------")
            exit(1)

        # flush after the player stopped playing
        Logger.instance().flush()
        print("[Qrogue] Successfully flushed all logs and shut down the game without any problems. See you next time!")
    else:
        print(f"[Qrogue] Error #{return_code}:")
        if return_code == 1:
            print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
                  "to your save files). Using special characters in the path could also cause this error so if the path is "
                  "valid please consider using another one without special characters.")

    if __CONSOLE_ARGUMENT not in sys.argv:
        print()
        input("[Qrogue] Press ENTER to close the application")

    exit(return_code)
