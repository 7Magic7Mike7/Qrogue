from typing import List, Union, Tuple, Optional

from qrogue.game.logic.actors.controllables import Robot
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, CollectibleFactory, Instruction
from qrogue.util import Logger, MyRandom


class ExplicitTargetDifficulty:
    """
    A TargetDifficulty that doesn't create StateVectors based on a Robot's possibilities but by choosing from a pool
    of explicitly provided StateVectors
    """

    def __init__(self, stv_pool: List[StateVector], reward: Optional[Union[CollectibleFactory, Collectible]] = None,
                 ordered: bool = False):
        """

        :param stv_pool: list of StateVectors to choose from
        :param reward: factory for creating a reward or a specific reward (Collectible)
        :param ordered: whether StateVectors should be chosen in order or randomly from the given stv_pool
        """
        self.__pool = stv_pool
        self.__ordered = ordered
        self.__order_index = -1
        if reward is None:
            self.__reward_factory = None
        elif isinstance(reward, CollectibleFactory):
            self.__reward_factory = reward
        else:
            self.__reward_factory = CollectibleFactory([reward])

    @property
    def has_reward_factory(self) -> bool:
        return self.__reward_factory is not None

    def create_statevector(self, robot: Robot, rm: MyRandom) -> StateVector:
        if self.__ordered or rm is None:
            self.__order_index += 1
            if self.__order_index >= len(self.__pool):
                self.__order_index = 0
            stv = self.__pool[self.__order_index]
        else:
            stv = rm.get_element(self.__pool, msg="ExplicitTargetDiff_selectStv")

        if stv.num_of_qubits != robot.num_of_qubits:
            Logger.instance().warn(f"Stv (={stv}) from pool does not have correct number of qubits (="
                                   f"{robot.num_of_qubits})!", show=False, from_pycui=False)
        return stv

    def produce_reward(self, rm: MyRandom) -> Optional[Collectible]:
        if self.__reward_factory is None:
            return None
        return self.__reward_factory.produce(rm)

    def copy_pool(self) -> List[StateVector]:
        return self.__pool.copy()
