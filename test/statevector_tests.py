import numpy as np

from game.logic.qubit import StateVector

stv = StateVector([1 / np.sqrt(2), 0 + 0j, 0 + 0j, 1 / np.sqrt(2)])
stv.extend(1)
print(stv)