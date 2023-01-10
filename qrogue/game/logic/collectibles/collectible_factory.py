from typing import List, Optional

from qrogue.game.logic.collectibles import Collectible, consumable, instruction as gates, pickup, ShopItem
from qrogue.util import Logger, MyRandom, RandomManager, ShopConfig


class CollectibleFactory:
    @staticmethod
    def empty() -> "CollectibleFactory":
        return CollectibleFactory([None])

    def __init__(self, pool: List[Collectible]) -> None:
        if pool is None or len(pool) < 1:
            Logger.instance().throw(Exception(f"invalid pool for CollectibleFactory: {pool}"))
        self.__pool = pool.copy()
        self.__rm = RandomManager.create_new()
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
    def default():
        return CollectibleFactory(pool=[
            gates.HGate(), gates.XGate(), #gates.YGate(), gates.ZGate(),
            gates.CXGate(), gates.SwapGate(),
        ])


class ShopFactory:
    @staticmethod
    def default() -> "ShopFactory":
        special_pool = [gates.HGate(), gates.XGate(), gates.HGate()]
        common_pool = [pickup.Key(1), pickup.Key(2), consumable.EnergyRefill(20)]
        return ShopFactory(common_pool, special_pool, quality_level=1)

    def __init__(self, common_pool: List[Collectible], special_pool: List[Collectible], quality_level: int = 1,
                 min_items: int = 2, max_items: int = 5, discount: bool = False):
        """

        :param common_pool: contains all Pickups the shop can sell
        :param special_pool: contains all Gates (and later other special Collectibles) that the Shop could offer
        :param quality_level: how good the Shop should be, i.e. higher quality = better ShopItems
        :param min_items: minimum number of ShopItems available in the Shop
        :param max_items: maximum number of ShopItems available in the Shop
        :param discount: whether the ShopItems are 50% off or not
        """
        self.__common_pool = common_pool
        self.__special_pool = special_pool
        self.__quality_level = quality_level
        self.__min_items = min_items
        self.__max_items = max_items
        self.__discount = discount

    def produce(self, rm: MyRandom, num_of_items: int = 0) -> List[ShopItem]:
        """
        Produces a random list of ShopItems based on the factory's parameter. Said parameter are not changed allowing
        to produce multiple lists with the same factory. The only thing that obviously changes is the current seed of
        its random manager.

        :param rm: decides about the randomness
        :param num_of_items: if set to 0 or less, takes a random number of items in the factory's [min, max[ range
        :return: a list of randomly picked ShopItems based on the factory's parameter
        """
        shop_items = []
        special_items = self.__special_pool.copy()
        pickups = self.__common_pool.copy()
        if num_of_items <= 0:
            num_of_items = rm.get_int(self.__min_items, self.__max_items, msg="ShopFactory.produce_numOfItems")
        quality_level = self.__quality_level
        while len(shop_items) <= num_of_items:
            if quality_level > 0:
                # with a certain probability the next item will be a special one (1 is guaranteed at quality_level == 1)
                gets_special = rm.get(msg="ShopFactory_specialItemProb") < 1.0 / quality_level
            else:
                gets_special = False

            if gets_special and self.__special_pool is not None and len(special_items) > 0:
                item = rm.get_element(special_items, remove=True, msg="ShopFactory_specialItemSelect")
            else:
                item = rm.get_element(pickups, remove=False, msg="ShopFactory_pickupSelect")

            # calculate the price with possibly a small variation
            if self.__discount:
                price = round(item.default_price() / 2)
            else:
                price_sigma = max(ShopConfig.base_unit(), item.default_price() * 0.1)
                price = item.default_price() + round(rm.get(-price_sigma, +price_sigma, msg="ShopFactory_price"))

            shop_items.append(ShopItem(item, price))
            quality_level -= 1
        return shop_items
