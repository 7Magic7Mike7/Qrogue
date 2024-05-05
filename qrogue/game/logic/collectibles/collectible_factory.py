from typing import List, Optional

from qrogue.game.logic.collectibles import Collectible, consumable, instruction as gates
from qrogue.util import Logger, MyRandom, RandomManager


class CollectibleFactory:
    @staticmethod
    def empty() -> "CollectibleFactory":
        return CollectibleFactory([None])

    def __init__(self, pool: List[Collectible]) -> None:
        if pool is None or len(pool) < 1:
            Logger.instance().throw(Exception(f"invalid pool for CollectibleFactory: {pool}"))
        self.__pool = pool.copy()
        self.__order_index = -1

    @property
    def pool_copy(self) -> List[Collectible]:   # todo make protected instead of public?
        return self.__pool.copy()

    def __produce(self, rm: Optional[MyRandom], remove: bool = False) -> Optional[Collectible]:
        if len(self.__pool) <= 0:
            return None

        if rm:
            return rm.get_element(self.__pool, remove=remove, msg="CollectibleFactory.__produce")
        else:
            self.__order_index += 1
            if self.__order_index >= len(self.__pool):
                self.__order_index = 0
            elem = self.__pool[self.__order_index]
            if remove:
                self.__pool.remove(elem)
            return elem

    def produce(self, rm: Optional[MyRandom] = None) -> Optional[Collectible]:
        return self.__produce(rm, remove=False)

    def produce_multiple(self, rm: Optional[MyRandom], num_of_elements: int, unique_elements: bool = True) \
            -> List[Collectible]:
        """
        Produces a list with multiple Collectibles. If unique_elements is True and num_of_elements is greater than the
        number of Collectibles available in the factory's pool, we start over after depleting the pool. In any case if
        the pool doesn't contain any Collectible, an empty list is returned.

        :param rm: MyRandom for random selection from pool if wanted, None implies ordered selection
        :param num_of_elements: how many Collectibles we want to produce
        :param unique_elements: whether the selected Collectibles should be unique (if possible)
        :return: a list with the specified number of elements or an empty list if the factory cannot produce
        Collectibles
        """
        if len(self.__pool) <= 0:
            return []

        if unique_elements:
            temp = self.pool_copy
            elements = []
            while len(elements) < num_of_elements:
                elem = self.__produce(rm, remove=True)
                if elem is not None:
                    elements.append(elem)
                    if len(self.__pool) <= 0:
                        self.__pool = temp.copy()
            self.__pool = temp
            return elements
        else:
            return [self.__produce(rm, remove=False) for _ in range(num_of_elements)]


class OrderedCollectibleFactory(CollectibleFactory):
    """
    Same as CollectibleFactory but instead of defaulting to random production this
    class defaults to ordered production
    """
    @staticmethod
    def from_factory(factory: CollectibleFactory):
        return OrderedCollectibleFactory(factory.pool_copy)

    def __init__(self, pool: List[Collectible]):
        super().__init__(pool)

    def produce(self, rm: Optional[MyRandom] = None) -> Collectible:
        return super(OrderedCollectibleFactory, self).produce()

    def produce_multiple(self, rm: Optional[MyRandom], num_of_elements: int, unique_elements: bool = True) \
            -> List[Collectible]:
        return super(OrderedCollectibleFactory, self).produce_multiple(None, num_of_elements, unique_elements)


class GateFactory:
    @staticmethod
    def default() -> CollectibleFactory:
        return CollectibleFactory(pool=[
            gates.HGate(), gates.XGate(), #gates.YGate(), gates.ZGate(),
            gates.CXGate(), gates.SwapGate(),
        ])

    @staticmethod
    def quantum() -> CollectibleFactory:
        return CollectibleFactory(pool=[
            gates.HGate(), gates.SGate(), gates.YGate(), gates.ZGate(),
        ])
