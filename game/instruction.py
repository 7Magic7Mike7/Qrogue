
# wrapper for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
class Instruction:
    def __init__(self, instruction, qargs: "list of ints", cargs: "list of ints" = None):
        self.instruction = instruction
        self.qargs = qargs
        if cargs is None:
            self.cargs = []
        else:
            self.cargs = cargs
