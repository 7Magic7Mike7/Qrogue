#D:\Programs\anaconda3\envs\Qrogue
# This is a sample Python script.
import random
import sys

from game.game import GameHandler
from util.config import Config
from util.key_logger import KeyLogger
from util.logger import Logger


__CONSOLE_ARGUMENT = "--from-console"
__DEBUG_ARGUMENT = "--debug"

note = """
Climate Crisis Narrative? E.g. the game plays on earth in 2070, most places have been destroyed 
and the remaining lives are weird mutations/... 
The goal is to find parts of a Quantum Computer (inspiration from Entanglion) so we are able to 
turn back time so we can "stop" the climate crisis and live on a healthy planet?
"""

return_code = Config.load()     # NEEDS TO BE THE FIRST THING WE DO!
if return_code == 0:
    if __DEBUG_ARGUMENT in sys.argv:
        Config.activate_debugging()
    seed = random.randint(0, Config.MAX_SEED)
    print(f"[Qrogue] Starting game with seed = {seed}")
    game = GameHandler(seed)
    game.start()

    # flush after the player stopped playing
    Logger.instance().flush()
    KeyLogger.instance().flush_if_useful()
else:
    print(f"[Qrogue] Error #{return_code}:")
    if return_code == 1:
        print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
          "to your save files). Using special characters in the path could also cause this error so if the path is "
          "valid please consider using another one without special characters.")

if __CONSOLE_ARGUMENT not in sys.argv:
    print()
    input("[Qrogue] Press ENTER to close the application")
