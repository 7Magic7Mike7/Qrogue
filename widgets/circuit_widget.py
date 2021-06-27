
from py_cui.widgets import BlockLabel

from game.actors.player import Player
from game.logic.instruction import HGate
from util.logger import Logger


class CircuitWidget:

    def __init__(self, circuit_widget: BlockLabel, logger: Logger):
        self.__widget = circuit_widget
        self.__logger = logger
        self.__player = None

    def set_player(self, player: Player):
        self.__player = player

    def render(self):
        if self.__player is not None:
            circ_str = ""       # todo prepend generator!
            instructions = self.__player.instructions
            if len(instructions) > 0:
                rows = ["|" + HGate(0).abbreviation(0) + "|---"] * self.__player.num_of_qubits
                for inst in instructions:
                    used_qubits = [False] * self.__player.num_of_qubits
                    max_len = 0
                    for q in inst.qargs:
                        used_qubits[q] = True
                        inst_str = f"--<{inst.abbreviation(q)}>--"
                        max_len = max(max_len, len(inst_str))
                        rows[q] += inst_str
                    for i in range(len(used_qubits)):
                        if not used_qubits[i]:
                            rows[i] += ("-" * max_len)
            else:
                rows = ["-------"] * self.__player.num_of_qubits
            for row in rows:
                circ_str += row + "---(enemy gen?)" + "\n" # perhaps show the generator of the enemy, but I guess it
                # is not a good idea since the player has no impact on this and should focus on the "main" direction
                # of the circuit
            self.__widget.set_title(circ_str)