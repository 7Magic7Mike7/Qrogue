#D:\Programs\anaconda3\envs\Qrogue
# This is a sample Python script.
import random
import sys

from game.game import GameHandler
from util.config import Config
from util.key_logger import KeyLogger
from util.logger import Logger

note = """
Climate Crisis Narrative? E.g. the game plays on earth in 2070, most places have been destroyed 
and the remaining lives are weird mutations/... 
The goal is to find parts of a Quantum Computer (inspiration from Entanglion) so we are able to 
turn back time so we can "stop" the climate crisis and live on a healthy planet?
"""

return_code = Config.load()
if return_code == 0:
    seed = random.randint(0, sys.maxsize)
    game = GameHandler(seed)
    game.start()
    # flush after the player stopped playing
    Logger.instance().flush()
    KeyLogger.instance().flush(force=False)
else:
    print(f"[Qrogue] Error #{return_code}:")
    if return_code == 1:
        print("qrogue.config is invalid. Please check if the second line describes a valid path (the path "
          "to your save files). Using special characters in the path could also cause this error so if the path is "
          "valid please consider using another one without special characters.")
