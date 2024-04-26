import numpy as np
import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.logic.actors.puzzles import is_puzzle_solvable

from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Instruction

stv = StateVector([1 / np.sqrt(2), 0 + 0j, 0 + 0j, 1 / np.sqrt(2)])
#stv.extend(1)
#print(stv)


input_stv_ = StateVector([0, 0, 0, 0, complex(0, -1), 0, 0, 0])
target_stv_ = Instruction.compute_stv([
    gates.HGate().setup([1]),
], 3)

#gate_list_ = [gates.XGate(), gates.CXGate(), gates.HGate(), gates.SGate()]     # this order returns True
gate_list_ = [gates.HGate(), gates.SGate(), gates.XGate(), gates.CXGate()]      # but this order returns False

ret, circuit = is_puzzle_solvable(input_stv_, target_stv_, gate_list_)
print(ret)
print(circuit)
