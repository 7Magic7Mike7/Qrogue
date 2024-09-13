from typing import List, Tuple, Dict

import qrogue.game.logic.collectibles.instruction as gates
from qrogue.game.logic import PuzzleGenerator
from qrogue.game.logic.base import QuantumCircuit, StateVector
from qrogue.game.logic.collectibles import Score
from qrogue.test import test_util
from qrogue.util import RandomManager, StvDifficulty, DifficultyType
from qrogue.util.util_functions import cur_datetime


def produce_puzzle(seed: int, num_of_qubits: int, circuit_space: int, difficulty: StvDifficulty,
                   gate_list: List[gates.Instruction]) -> int:
    rm = RandomManager.create_new(seed)
    start_time = cur_datetime()
    PuzzleGenerator.generate_puzzle(rm, num_of_qubits, circuit_space, difficulty, gate_list, [gates.CXGate()], [Score()])
    duration = cur_datetime() - start_time
    return duration.microseconds


def analyze_puzzle_gen_speed(num_of_seeds: int = 100):
    """
        ~RESULT (1000 seeds)~
    Min:        72ms
    Q1:         94ms

    Median:     98ms
    Avg:       101ms

    Q3:        104ms
    Max:       290ms
    """
    num_of_qubits = 3
    circuit_space = 5
    gate_list = [gates.HGate(), gates.XGate(), gates.SGate(), gates.XGate(), gates.HGate()]

    diff_level = StvDifficulty.max_difficulty_level()
    difficulty = StvDifficulty.from_difficulty_level(diff_level)

    times = [produce_puzzle(seed, num_of_qubits, circuit_space, difficulty, gate_list) for seed in range(num_of_seeds)]

    times.sort()
    print(f"Min:     {int(times[0] / 1000)}ms")
    print(f"Q1:     {int(times[int(len(times) * 0.25)] / 1000)}ms")
    print(f"Median: {int(times[int(len(times) * 0.5)] / 1000)}ms")
    print(f"Avg:     {int(sum(times) / (1000 * len(times)))}ms")
    print(f"Q3:     {int(times[int(len(times) * 0.75)] / 1000)}ms")
    print(f"Max:     {int(times[-1] / 1000)}ms")


def analyze_puzzle_gen_success(num_of_seeds: int = 100, print_fails: bool = False, print_stats: bool = True):
    """
        ~RESULT (1000 seeds)~
    Success ratio: 93%
    Unique Stvs:   12%

        ~RESULT (100 seeds)~
    Success ratio: 93%
    Unique Stvs:   62%
    """

    num_of_qubits = 2
    circuit_space = 10
    num_of_gates = 4

    # available_gates = [gates.HGate(), gates.XGate(), gates.SGate(), gates.XGate(), gates.HGate(), gates.CXGate()]
    # available_gates = [gates.XGate(), gates.XGate(), gates.XGate()]
    available_gates = [gates.HGate(), gates.XGate(), gates.CXGate(), gates.SGate(), gates.YGate()]
    difficulty = test_util.ExplicitStvDifficulty({
        DifficultyType.CircuitExuberance: num_of_gates,
    }, num_of_qubits, circuit_space)

    unique_stvs: Dict[StateVector, Tuple[QuantumCircuit, List[int]]] = {}  # stv to circuit, seeds
    failed_seeds: List[Tuple[QuantumCircuit, int]] = []

    seeds = list(range(num_of_seeds))
    for seed in seeds:
        rm = RandomManager.create_new(seed)
        circuit = QuantumCircuit.from_bit_num(num_of_qubits)
        gate_list = PuzzleGenerator.prepare_from_gates(rm, num_of_qubits, circuit_space, difficulty,
                                                       available_gates, None, force_num_of_gates=True)
        for gate in gate_list: gate.append_to(circuit)

        if len(gate_list) < num_of_gates:
            failed_seeds.append((circuit, seed))
        else:
            cur_stv = gates.Instruction.compute_stv(gate_list, num_of_qubits)
            if cur_stv in unique_stvs:
                unique_stvs[cur_stv][1].append(seed)
            else:
                unique_stvs[cur_stv] = circuit, [seed]

    if print_stats:
        num_successful_seeds = len(seeds) - len(failed_seeds)
        print(f"Success ratio: {int(100 * num_successful_seeds / len(seeds))}%")
        print(f"Unique Stvs:   {int(100 * len(unique_stvs) / num_successful_seeds)}%")

    if print_fails:
        print("####### FAILS #######")
        for circuit, seed in failed_seeds:
            print(f"Seed: {seed}")
            print(circuit)
            print("________________________________________________________")


if __name__ == '__main__':
    if test_util.init_singletons(include_config=True):
        #analyze_puzzle_gen_speed()
        analyze_puzzle_gen_success()
    else:
        raise Exception("Could not initialize singletons")
