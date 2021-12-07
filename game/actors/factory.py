from abc import ABC, abstractmethod

from game.actors.player import Player as PlayerActor
from game.actors.enemy import Enemy as EnemyActor, DummyEnemy
from game.actors.riddle import Riddle
from game.actors.target import Target
from game.collectibles.pickup import Coin, Key
from game.logic import instruction as gates
from game.logic.qubit import StateVector

from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from game.map.navigation import Direction
from util.my_random import RandomManager, MyRandom


class TargetDifficulty:
    """
    A class that handles all parameters that define the difficulty of a fight.
    """

    def __init__(self, num_of_instructions: int, reward_pool: "list of Collectibles"):
        """

        :param num_of_instructions: num of instructions used to create a statevector
        :param reward_pool: list of possible rewards for winning against an enemy of this difficulty
        """
        self.__num_of_instructions = num_of_instructions
        self.__reward_pool = reward_pool

    @property
    def reward_pool(self):
        return self.__reward_pool

    def create_statevector(self, player: PlayerActor) -> StateVector:
        """
        Creates a StateVector that is reachable for the player.

        :param player: defines the number of qubits and usable instructions for creating the statevector
        :return: the created StateVector
        """
        num_of_qubits = player.num_of_qubits
        circuit = QuantumCircuit(num_of_qubits, num_of_qubits)
        rand = RandomManager.instance()
        qubits = list(range(num_of_qubits))

        # choose random circuits on random qubits and cbits
        instruction_pool = player.get_available_instructions()
        for i in range(self.__num_of_instructions):
            remove = len(instruction_pool) - (self.__num_of_instructions - i) >= 0
            instruction = rand.get_element(instruction_pool, remove=remove)
            if instruction.num_of_qubits > 1:
                while instruction.use_qubit(rand.get_element(qubits, remove=True)):
                    pass
                qubits = list(range(num_of_qubits))
            else:
                instruction.use_qubit(rand.get_element(qubits))
            instruction.append_to(circuit)
        simulator = StatevectorSimulator()
        compiled_circuit = transpile(circuit, simulator)
        # We only do 1 shot since we don't need any measurement but the StateVector
        job = simulator.run(compiled_circuit, shots=1)
        return StateVector(job.result().get_statevector())


class RiddleDifficulty(TargetDifficulty):
    def __init__(self, num_of_instructions: int, reward_pool: "list of Collectibles", min_attempts: int = 1,
                 max_attempts: int = 10):
        super().__init__(num_of_instructions, reward_pool)
        self.__min_attempts = min_attempts
        self.__max_attempts = max_attempts

    def get_attempts(self, rm: MyRandom) -> int:
        return rm.get_int(self.__min_attempts, self.__max_attempts)


class DummyTargetDifficulty(TargetDifficulty):
    """
    Dummy implementation of a FightDifficulty class for testing.
    """

    def __init__(self):
        super(DummyTargetDifficulty, self).__init__(2, [Coin(1), Coin(3)])


class TargetFactory(ABC):
    def __init__(self, start_callback: "(Player, Target, Direction)", difficulty: TargetDifficulty):
        self.__start_callback = start_callback
        self.__difficulty = difficulty
        self.__rm = RandomManager.create_new()

    @property
    def _difficulty(self) -> TargetDifficulty:
        return self.__difficulty

    @property
    def _rm(self) -> MyRandom:
        return self.__rm

    def start(self, player: PlayerActor, target: Target, direction: Direction):
        self.__start_callback(player, target, direction)

    @abstractmethod
    def produce(self, player: PlayerActor, flee_chance: float) -> Target:
        pass


class EnemyFactory(TargetFactory):
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, start_fight_callback: "(Player, Target, Direction)", difficulty: TargetDifficulty):
        """

        :param start_fight_callback: a method for starting a fight
        :param difficulty: difficulty of the enemy we produce
        """
        super(EnemyFactory, self).__init__(start_fight_callback, difficulty)

    def produce(self, player: PlayerActor, flee_chance: float) -> EnemyActor:
        """
        Creates an enemy based on the number of qubits the provided player has.

        :param flee_chance: chance of the player to flee from the fight
        :param player: the player the enemy should fight against
        :return: a freshly created enemy
        """
        stv = self._difficulty.create_statevector(player)
        reward = self._rm.get_element(self._difficulty.reward_pool)
        return DummyEnemy(stv, reward, flee_chance)


class RiddleFactory(TargetFactory):
    @staticmethod
    def default(callback) -> "RiddleFactory":
        reward_pool = [gates.CXGate(), gates.HGate, gates.XGate, gates.SwapGate, Coin(11), Key(5)]
        difficulty = RiddleDifficulty(num_of_instructions=4, reward_pool=reward_pool, min_attempts=4, max_attempts=9)
        return RiddleFactory(callback, difficulty)

    def __init__(self, open_riddle_callback: "(Player, Target, Direction)", difficulty: RiddleDifficulty):
        super().__init__(open_riddle_callback, difficulty)

    def produce(self, player: PlayerActor, flee_chance: float = 1.0) -> Riddle:
        stv = self._difficulty.create_statevector(player)
        reward = self._rm.get_element(self._difficulty.reward_pool)
        attempts = self._difficulty.get_attempts(self._rm)
        return Riddle(stv, reward, attempts)
