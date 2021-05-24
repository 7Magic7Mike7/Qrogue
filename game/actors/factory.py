
from game.actors.player import Player as PlayerActor
from game.actors.enemy import Enemy as EnemyActor, DummyEnemy
from game.callbacks import OnWalkCallback
from game.collectibles.pickup import Coin
from game.logic.qubit import StateVector

from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from util.my_random import RandomManager


class FightDifficulty:
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
            instruction = rand.get_element(instruction_pool, remove=True)
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


class DummyFightDifficulty(FightDifficulty):
    """
    Dummy implementation of a FightDifficulty class for testing.
    """

    def __init__(self):
        super(DummyFightDifficulty, self).__init__(2, [Coin(1), Coin(3)])


class EnemyFactory:
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, start_fight_callback: OnWalkCallback, difficulty: FightDifficulty):
        """

        :param start_fight_callback: a method for starting a fight
        :param difficulty: difficulty of the enemy we produce
        """
        self.__start_fight_callback = start_fight_callback
        self.__difficulty = difficulty
        self.__rm = RandomManager.create_new()

    @property
    def callback(self):
        """
        :return: the callback method to start a fight
        """
        return self.__start_fight_callback

    def get_enemy(self, player: PlayerActor, flee_chance: float) -> EnemyActor:
        """
        Creates an enemy based on the number of qubits the provided player has.

        :param flee_chance: chance of the player to flee from the fight
        :param player: the player the enemy should fight against
        :return: a freshly created enemy
        """
        stv = self.__difficulty.create_statevector(player)
        reward = self.__rm.get_element(self.__difficulty.reward_pool)
        return DummyEnemy(stv, reward, flee_chance)
