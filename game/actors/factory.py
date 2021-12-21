from game.actors.boss import Boss as BossActor
from game.actors.robot import Robot
from game.actors.enemy import Enemy as EnemyActor, DummyEnemy
from game.actors.riddle import Riddle
from game.actors.target import Target
from game.collectibles import pickup
from game.collectibles.collectible import Collectible
from game.logic import instruction as gates
from game.logic.instruction import Instruction
from game.logic.qubit import StateVector
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

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        """
        Creates a StateVector that is reachable for the robot.

        :param robot: defines the number of qubits and usable instructions for creating the statevector
        :param rm:
        :return: the created StateVector
        """
        num_of_qubits = robot.num_of_qubits

        # choose random circuits on random qubits and cbits
        instruction_pool = robot.get_available_instructions()
        instructions = []
        num_of_instructions = min(self.__num_of_instructions, robot.circuit_space)
        for i in range(num_of_instructions):
            qubits = list(range(num_of_qubits))
            #remove = len(instruction_pool) - (self.__num_of_instructions - i) >= 0
            #if not remove:
            #    Logger.instance().throw(Exception(
            #        "this should always remove because else we would duplicate instructions"))
            instruction = rm.get_element(instruction_pool, remove=True)
            while instruction.use_qubit(rm.get_element(qubits, remove=True)):
                pass
            instructions.append(instruction)
        return StateVector.from_gates(instructions, num_of_qubits)


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
        super(DummyTargetDifficulty, self).__init__(2, [pickup.Coin(1), pickup.Coin(3)])


class EnemyFactory:
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, robot: Robot, start_fight_callback: "(Robot, Target, Direction)",
                 difficulty: TargetDifficulty):
        """

        :param difficulty: difficulty of the enemy we produce
        """
        #self.__robot = robot
        self.__difficulty = difficulty
        self.__start_fight = start_fight_callback

    def produce(self, robot: Robot, rm: MyRandom, flee_chance: float) -> EnemyActor:
        """
        Creates an enemy based on the number of qubits the provided robot has.

        :param robot:
        :param rm:
        :param flee_chance: chance of the robot to flee from the fight
        :return: a freshly created enemy
        """
        stv = self.__difficulty.create_statevector(robot, rm)
        reward = rm.get_element(self.__difficulty.reward_pool)
        return DummyEnemy(stv, reward, flee_chance)

    def start(self, robot: Robot, target: Target, direction: Direction):
        self.__start_fight(robot, target, direction)


class RiddleFactory:
    @staticmethod
    def default(robot: Robot) -> "RiddleFactory":
        reward_pool = [gates.CXGate(), gates.HGate, gates.XGate, gates.SwapGate, pickup.Coin(11), pickup.Key(5)]
        difficulty = RiddleDifficulty(num_of_instructions=4, reward_pool=reward_pool, min_attempts=4, max_attempts=9)
        return RiddleFactory(robot, difficulty)

    def __init__(self, robot: Robot, difficulty: RiddleDifficulty):
        self.__robot = robot
        self.__difficulty = difficulty
        self.__rm = RandomManager.create_new()

    def produce(self) -> Riddle:
        stv = self.__difficulty.create_statevector(self.__robot, self.__rm)
        reward = self.__rm.get_element(self.__difficulty.reward_pool)
        attempts = self.__difficulty.get_attempts(self.__rm)
        return Riddle(stv, reward, attempts)


class BossFactory:
    @staticmethod
    def default(robot: Robot) -> "BossFactory":
        pool = [gates.CXGate(), gates.SwapGate(), pickup.Coin(30)]
        return BossFactory(robot, pool)

    def __init__(self, robot: Robot, reward_pool: [Collectible]):
        self.__robot = robot
        self.__reward_pool = reward_pool
        self.__rm = RandomManager.create_new()

    def produce(self, include_gates: [Instruction]) -> BossActor:
        used_gates = []
        qubit_count = [0] * self.__robot.num_of_qubits
        qubits = list(range(self.__robot.num_of_qubits))

        for g in include_gates:
            gate = g.copy()
            self.__prepare_gate(gate, qubit_count, qubits)
            used_gates.append(gate)

        usable_gates = self.__robot.get_available_instructions()
        while len(usable_gates) > 0:
            gate = self.__rm.get_element(usable_gates, remove=True)
            self.__prepare_gate(gate, qubit_count, qubits)
            used_gates.append(gate)

        reward = self.__rm.get_element(self.__reward_pool)
        return BossActor(StateVector.from_gates(used_gates, self.__robot.num_of_qubits), reward)

    def __prepare_gate(self, gate: Instruction, qubit_count, qubits):
        gate_qubits = qubits.copy()
        while True:
            qubit = self.__rm.get_element(gate_qubits, remove=True)
            qubit_count[qubit] += 1
            if qubit_count[qubit] >= self.__robot.circuit_space:
                qubits.remove(qubit)
            if not gate.use_qubit(qubit):
                return
